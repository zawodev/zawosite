import json
import asyncio
from typing import Dict, List
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Player, Creature, Spell
from .models import Battle, BattleParticipant, BattleAction
from .battle_engine import BattleEngine, BattleMatchmaker


class BattleConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer dla walk online"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.battle_id = None
        self.battle_group_name = None
        self.user = None
        self.player = None
    
    async def connect(self):
        """Połączenie WebSocket"""
        # Sprawdź autoryzację
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Pobierz gracza
        try:
            self.player = await database_sync_to_async(Player.objects.get)(user=self.user)
        except Player.DoesNotExist:
            await self.close()
            return
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to battle server'
        }))
    
    async def disconnect(self, close_code):
        """Rozłączenie WebSocket"""
        if self.battle_group_name:
            await self.channel_layer.group_discard(
                self.battle_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Obsługa wiadomości od klienta"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'create_battle':
                await self.create_battle(data)
            elif message_type == 'join_battle':
                await self.join_battle(data)
            elif message_type == 'select_move':
                await self.select_move(data)
            elif message_type == 'confirm_ready':
                await self.confirm_ready(data)
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            await self.send_error(f"Error processing message: {str(e)}")
    
    async def create_battle(self, data):
        """Tworzy nową walkę"""
        battle_type = data.get('battle_type', 'friendly')
        team_creatures = data.get('team_creatures', [])
        
        if not team_creatures:
            await self.send_error("No creatures selected")
            return
        
        # Weryfikuj że gracz posiada wszystkie creatures
        valid_creatures = await self.validate_player_creatures(team_creatures)
        if not valid_creatures:
            await self.send_error("Invalid creatures selected")
            return
        
        # Utwórz battle
        battle = await database_sync_to_async(BattleMatchmaker.create_battle)(
            self.player, battle_type
        )
        
        self.battle_id = str(battle.id)
        self.battle_group_name = f"battle_{self.battle_id}"
        
        # Dołącz do grupy
        await self.channel_layer.group_add(
            self.battle_group_name,
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'battle_created',
            'battle_id': self.battle_id,
            'battle_type': battle_type,
            'waiting_for_opponent': True
        }))
    
    async def join_battle(self, data):
        """Dołącza do istniejącej walki"""
        battle_id = data.get('battle_id')
        team_creatures = data.get('team_creatures', [])
        opponent_creatures = data.get('opponent_creatures', [])  # creatures pierwszego gracza
        
        if not battle_id:
            await self.send_error("Battle ID required")
            return
        
        # Weryfikuj creatures
        valid_creatures = await self.validate_player_creatures(team_creatures)
        if not valid_creatures:
            await self.send_error("Invalid creatures selected")
            return
        
        try:
            battle = await database_sync_to_async(Battle.objects.get)(id=battle_id)
        except Battle.DoesNotExist:
            await self.send_error("Battle not found")
            return
        
        # Dołącz do walki
        success = await database_sync_to_async(BattleMatchmaker.join_battle)(
            battle, self.player, opponent_creatures, team_creatures
        )
        
        if not success:
            await self.send_error("Cannot join battle")
            return
        
        self.battle_id = battle_id
        self.battle_group_name = f"battle_{battle_id}"
        
        # Dołącz do grupy
        await self.channel_layer.group_add(
            self.battle_group_name,
            self.channel_name
        )
        
        # Wyślij informację o rozpoczęciu walki do obu graczy
        participants_data = await self.get_battle_participants_data(battle)
        
        await self.channel_layer.group_send(
            self.battle_group_name,
            {
                'type': 'battle_started',
                'battle_id': battle_id,
                'participants': participants_data
            }
        )
    
    async def select_move(self, data):
        """Wybór ruchu gracza"""
        if not self.battle_id:
            await self.send_error("Not in battle")
            return
        
        creature_id = data.get('creature_id')
        spell_id = data.get('spell_id')
        target_id = data.get('target_id')  # opcjonalny
        
        try:
            battle = await database_sync_to_async(Battle.objects.get)(id=self.battle_id)
            participant = await database_sync_to_async(
                BattleParticipant.objects.get
            )(battle=battle, creature_id=creature_id, player=self.player)
            
            spell = await database_sync_to_async(Spell.objects.get)(id=spell_id)
            
            # Sprawdź czy creature zna ten spell
            knows_spell = await database_sync_to_async(
                lambda: participant.creature.known_spells.filter(spell=spell).exists()
            )()
            
            if not knows_spell:
                await self.send_error("Creature doesn't know this spell")
                return
            
            # Ustaw wybór
            participant.selected_spell = spell
            if target_id:
                try:
                    target = await database_sync_to_async(
                        BattleParticipant.objects.get
                    )(battle=battle, creature_id=target_id)
                    participant.selected_target = target
                except BattleParticipant.DoesNotExist:
                    pass
            
            await database_sync_to_async(participant.save)()
            
            await self.send(text_data=json.dumps({
                'type': 'move_selected',
                'creature_id': creature_id,
                'spell_id': spell_id,
                'target_id': target_id
            }))
            
        except Exception as e:
            await self.send_error(f"Error selecting move: {str(e)}")
    
    async def confirm_ready(self, data):
        """Potwierdza gotowość gracza do wykonania tury"""
        if not self.battle_id:
            await self.send_error("Not in battle")
            return
        
        try:
            battle = await database_sync_to_async(Battle.objects.get)(id=self.battle_id)
            
            # Oznacz wszystkie creatures gracza jako gotowe
            participants = await database_sync_to_async(lambda: list(
                BattleParticipant.objects.filter(battle=battle, player=self.player)
            ))()
            
            for participant in participants:
                if participant.selected_spell and participant.is_alive:
                    participant.has_confirmed_move = True
                    await database_sync_to_async(participant.save)()
            
            # Sprawdź czy obaj gracze są gotowi
            all_participants = await database_sync_to_async(lambda: list(
                BattleParticipant.objects.filter(battle=battle)
            ))()
            
            team1_ready = all(p.has_confirmed_move or not p.is_alive 
                             for p in all_participants if p.team == 1)
            team2_ready = all(p.has_confirmed_move or not p.is_alive 
                             for p in all_participants if p.team == 2)
            
            if team1_ready and team2_ready:
                # Wykonaj turę
                await self.execute_turn(battle)
            else:
                # Powiadom o gotowości
                await self.channel_layer.group_send(
                    self.battle_group_name,
                    {
                        'type': 'player_ready',
                        'player_id': self.player.id,
                        'team1_ready': team1_ready,
                        'team2_ready': team2_ready
                    }
                )
                
        except Exception as e:
            await self.send_error(f"Error confirming ready: {str(e)}")
    
    async def execute_turn(self, battle):
        """Wykonuje turę i wysyła wyniki"""
        try:
            # Wykonaj turę
            actions = await database_sync_to_async(BattleEngine.execute_turn)(battle)
            
            # Przygotuj dane akcji dla klienta
            actions_data = []
            for action in actions:
                action_data = {
                    'action_type': action.action_type,
                    'caster': {
                        'creature_id': action.caster.creature.id,
                        'name': action.caster.creature.name
                    },
                    'spell_name': action.spell_used.name if action.spell_used else None,
                    'damage_amount': action.damage_amount,
                    'heal_amount': action.heal_amount,
                }
                
                if action.target:
                    action_data['target'] = {
                        'creature_id': action.target.creature.id,
                        'name': action.target.creature.name,
                        'hp_after': action.target_hp_after,
                        'alive_after': action.target_alive_after
                    }
                
                actions_data.append(action_data)
            
            # Sprawdź czy walka się skończyła
            winner = await database_sync_to_async(BattleEngine.check_battle_end)(battle)
            
            if winner:
                # Zastosuj wyniki walki
                await database_sync_to_async(BattleEngine.apply_battle_results)(battle, winner)
                
                await self.channel_layer.group_send(
                    self.battle_group_name,
                    {
                        'type': 'battle_ended',
                        'winner': winner,
                        'actions': actions_data
                    }
                )
            else:
                # Wyślij wyniki tury
                await self.channel_layer.group_send(
                    self.battle_group_name,
                    {
                        'type': 'turn_results',
                        'turn_number': battle.current_turn - 1,
                        'actions': actions_data
                    }
                )
                
        except Exception as e:
            await self.send_error(f"Error executing turn: {str(e)}")
    
    # Event handlers dla group_send
    async def battle_started(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def turn_results(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def battle_ended(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def player_ready(self, event):
        await self.send(text_data=json.dumps(event))
    
    # Helper methods
    async def send_error(self, message: str):
        """Wysyła błąd do klienta"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    async def validate_player_creatures(self, creature_ids: List[int]) -> bool:
        """Sprawdza czy gracz posiada podane creatures"""
        try:
            count = await database_sync_to_async(
                Creature.objects.filter(
                    id__in=creature_ids, 
                    owner=self.player
                ).count
            )()
            return count == len(creature_ids)
        except:
            return False
    
    async def get_battle_participants_data(self, battle):
        """Pobiera dane uczestników walki"""
        participants = await database_sync_to_async(lambda: list(
            BattleParticipant.objects.filter(battle=battle).select_related('creature', 'player')
        ))()
        
        participants_data = []
        for p in participants:
            participant_data = {
                'creature_id': p.creature.id,
                'name': p.creature.name,
                'max_hp': p.creature.max_hp,
                'current_hp': p.current_hp,
                'initiative': p.creature.initiative,
                'team': p.team,
                'player_name': p.player.user.username
            }
            participants_data.append(participant_data)
        
        return participants_data
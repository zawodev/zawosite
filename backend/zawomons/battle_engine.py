from typing import List, Dict, Optional, Tuple
import random
from .models import Battle, BattleParticipant, BattleAction
from .models import Creature, Spell
from django.utils import timezone


class BattleEngine:
    """Silnik walki - autorytatywne obliczenia po stronie serwera"""
    
    @staticmethod
    def calculate_damage(caster: BattleParticipant, target: BattleParticipant, spell: Spell) -> int:
        """Oblicza damage dla spell cast"""
        base_damage = caster.creature.damage
        
        # Znajdź spell effect dla damage
        spell_power = 0
        # TODO: Po dodaniu spell effects do modeli, tutaj będzie prawdziwe obliczenie
        # Na razie używamy prostej formuły
        spell_power = 25  # bazowy damage spella
        
        # Obliczenie finalnego damage
        total_damage = base_damage + spell_power
        
        # Dodaj losowość (±20%)
        variance = int(total_damage * 0.2)
        total_damage += random.randint(-variance, variance)
        
        return max(1, total_damage)  # minimum 1 damage
    
    @staticmethod
    def calculate_heal(caster: BattleParticipant, target: BattleParticipant, spell: Spell) -> int:
        """Oblicza heal amount dla healing spell"""
        # TODO: Po dodaniu spell effects
        base_heal = 30
        variance = int(base_heal * 0.15)
        heal_amount = base_heal + random.randint(-variance, variance)
        
        # Nie może leczyć ponad max HP
        current_hp = target.current_hp
        max_hp = target.creature.max_hp
        actual_heal = min(heal_amount, max_hp - current_hp)
        
        return max(0, actual_heal)
    
    @staticmethod
    def get_turn_order(participants: List[BattleParticipant]) -> List[BattleParticipant]:
        """Zwraca kolejność uczestników na podstawie inicjatywy"""
        alive_with_spells = [
            p for p in participants 
            if p.is_alive and p.selected_spell and p.has_confirmed_move
        ]
        
        # Sortuj po inicjatywie (malejąco), potem po levelu, exp i nazwie dla determinizmu
        return sorted(
            alive_with_spells,
            key=lambda p: (
                -p.total_initiative,
                -p.creature.level if hasattr(p.creature, 'level') else -p.creature.experience // 100,
                -p.creature.experience,
                p.creature.name
            )
        )
    
    @staticmethod
    def execute_turn(battle: Battle) -> List[BattleAction]:
        """Wykonuje jedną turę walki i zwraca listę akcji"""
        participants = list(battle.participants.all())
        turn_order = BattleEngine.get_turn_order(participants)
        
        actions = []
        action_counter = 0
        
        for participant in turn_order:
            if not participant.is_alive or not participant.selected_spell:
                continue
                
            spell = participant.selected_spell
            action_counter += 1
            
            # Określ cele na podstawie typu spella
            # TODO: Po dodaniu spell effects, tutaj będzie prawdziwe określanie celów
            targets = BattleEngine._get_spell_targets(participant, spell, participants)
            
            for target in targets:
                # Utwórz akcję spellcast
                action = BattleAction.objects.create(
                    battle=battle,
                    turn_number=battle.current_turn,
                    action_order=action_counter,
                    action_type='spell_cast',
                    caster=participant,
                    target=target,
                    spell_used=spell
                )
                
                # Oblicz i zastosuj efekt
                if spell.name.lower() in ['heal', 'cure', 'restore']:  # TODO: proper spell effect detection
                    heal_amount = BattleEngine.calculate_heal(participant, target, spell)
                    target.current_hp = min(target.creature.max_hp, target.current_hp + heal_amount)
                    action.heal_amount = heal_amount
                    action.action_type = 'heal_performed'
                else:
                    # Domyślnie damage
                    damage = BattleEngine.calculate_damage(participant, target, spell)
                    target.current_hp = max(0, target.current_hp - damage)
                    action.damage_amount = damage
                    action.action_type = 'damage_dealt'
                
                # Zapisz stan po akcji
                action.target_hp_after = target.current_hp
                action.target_alive_after = target.is_alive
                target.save()
                action.save()
                
                actions.append(action)
        
        # Reset wyboru ruchów na następną turę
        for participant in participants:
            participant.reset_move_selection()
        
        battle.current_turn += 1
        battle.save()
        
        return actions
    
    @staticmethod
    def _get_spell_targets(caster: BattleParticipant, spell: Spell, all_participants: List[BattleParticipant]) -> List[BattleParticipant]:
        """Określa cele spella na podstawie jego typu"""
        # TODO: Po dodaniu spell effects system, tutaj będzie prawdziwe określanie
        # Na razie proste określanie na podstawie nazwy i wybranego target
        
        if caster.selected_target:
            return [caster.selected_target]
        
        # Jeśli nie wybrano konkretnego celu, użyj domyślnej logiki
        if spell.name.lower() in ['heal', 'cure', 'restore']:
            # Leczenie - cel to sam siebie
            return [caster]
        else:
            # Atak - pierwszy żywy przeciwnik
            enemies = [p for p in all_participants if p.team != caster.team and p.is_alive]
            if enemies:
                return [enemies[0]]
            return []
    
    @staticmethod
    def check_battle_end(battle: Battle) -> Optional[str]:
        """Sprawdza czy walka się skończyła i zwraca zwycięzcę"""
        participants = list(battle.participants.all())
        
        team1_alive = any(p.is_alive for p in participants if p.team == 1)
        team2_alive = any(p.is_alive for p in participants if p.team == 2)
        
        if not team1_alive and not team2_alive:
            return "draw"
        elif not team1_alive:
            return "team2"
        elif not team2_alive:
            return "team1"
        
        return None  # walka trwa
    
    @staticmethod
    def apply_battle_results(battle: Battle, winner_team: str):
        """Stosuje efekty zakończonej walki (tylko dla ranked battles)"""
        if battle.battle_type != 'ranked':
            return  # friendly battles nie mają konsekwencji
        
        participants = list(battle.participants.all())
        
        for participant in participants:
            creature = participant.creature
            
            if winner_team == f"team{participant.team}":
                # Zwycięzca dostaje EXP
                exp_gain = 50 + (battle.current_turn * 5)  # więcej exp za dłuższe walki
                creature.experience += exp_gain
            else:
                # Przegrany dostaje mniej EXP
                exp_gain = 10 + (battle.current_turn * 2)
                creature.experience += exp_gain
            
            # Zaktualizuj HP do stanu po walce (tylko ranked battles)
            if battle.battle_type == 'ranked':
                creature.current_hp = participant.current_hp
                
                # Jeśli creature "umarło" w walce, zostaw mu 1 HP
                if creature.current_hp <= 0:
                    creature.current_hp = 1
            
            creature.save()
        
        battle.phase = 'finished'
        battle.finished_at = timezone.now()
        
        # Ustaw zwycięzcę
        if winner_team == "team1":
            battle.winner = battle.player1
        elif winner_team == "team2":
            battle.winner = battle.player2
        
        battle.save()


class BattleMatchmaker:
    """Zarządza tworzeniem i dołączaniem do walk"""
    
    @staticmethod
    def create_battle(player1, battle_type: str = 'friendly') -> Battle:
        """Tworzy nową walkę"""
        battle = Battle.objects.create(
            player1=player1,
            battle_type=battle_type,
            phase='waiting'
        )
        return battle
    
    @staticmethod
    def join_battle(battle: Battle, player2, team1_creatures: List[int], team2_creatures: List[int]) -> bool:
        """Dołącza drugiego gracza do walki z wybranymi creatures"""
        if battle.player2 is not None:
            return False  # battle już pełny
        
        battle.player2 = player2
        battle.phase = 'selection'
        battle.started_at = timezone.now()
        battle.save()
        
        # Dodaj creatures team 1 (player1)
        for creature_id in team1_creatures:
            try:
                creature = Creature.objects.get(id=creature_id, owner__user=battle.player1.user)
                BattleParticipant.objects.create(
                    battle=battle,
                    player=battle.player1,
                    creature=creature,
                    current_hp=creature.current_hp,
                    current_energy=creature.current_energy,
                    team=1
                )
            except Creature.DoesNotExist:
                continue
        
        # Dodaj creatures team 2 (player2)
        for creature_id in team2_creatures:
            try:
                creature = Creature.objects.get(id=creature_id, owner__user=player2.user)
                BattleParticipant.objects.create(
                    battle=battle,
                    player=player2,
                    creature=creature,
                    current_hp=creature.current_hp,
                    current_energy=creature.current_energy,
                    team=2
                )
            except Creature.DoesNotExist:
                continue
        
        return True
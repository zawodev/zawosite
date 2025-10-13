from rest_framework import serializers
from .models import Battle, BattleParticipant, BattleAction, Creature, Spell


class BattleSerializer(serializers.ModelSerializer):
    """Serializer dla Battle"""
    
    class Meta:
        model = Battle
        fields = ['id', 'battle_type', 'phase', 'player1', 'player2', 'winner', 
                 'current_turn', 'created_at', 'started_at', 'finished_at']
        read_only_fields = ['id', 'created_at', 'started_at', 'finished_at']


class BattleParticipantSerializer(serializers.ModelSerializer):
    """Serializer dla BattleParticipant"""
    creature_name = serializers.CharField(source='creature.name', read_only=True)
    player_name = serializers.CharField(source='player.user.username', read_only=True)
    
    class Meta:
        model = BattleParticipant
        fields = ['creature', 'creature_name', 'player_name', 'current_hp', 
                 'current_energy', 'initiative_bonus', 'team', 'is_alive', 'total_initiative']
        read_only_fields = ['is_alive', 'total_initiative']


class BattleActionSerializer(serializers.ModelSerializer):
    """Serializer dla BattleAction"""
    caster_name = serializers.CharField(source='caster.creature.name', read_only=True)
    target_name = serializers.CharField(source='target.creature.name', read_only=True)
    spell_name = serializers.CharField(source='spell_used.name', read_only=True)
    
    class Meta:
        model = BattleAction
        fields = ['turn_number', 'action_order', 'action_type', 'caster_name', 
                 'target_name', 'spell_name', 'damage_amount', 'heal_amount',
                 'target_hp_after', 'target_alive_after', 'timestamp']


class CreateBattleRequestSerializer(serializers.Serializer):
    """Serializer dla utworzenia nowej walki"""
    battle_type = serializers.ChoiceField(choices=['friendly', 'ranked'], default='friendly')
    team_creatures = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=6,  # maksymalnie 6 creatures w teamie
        help_text="Lista ID creatures dla drużyny gracza"
    )
    
    def validate_team_creatures(self, value):
        """Sprawdź czy wszystkie creatures należą do gracza"""
        user = self.context['request'].user
        try:
            player = user.player
        except:
            raise serializers.ValidationError("Player not found")
        
        # Sprawdź czy wszystkie creatures należą do gracza
        player_creature_ids = set(player.creatures.values_list('id', flat=True))
        provided_creature_ids = set(value)
        
        invalid_ids = provided_creature_ids - player_creature_ids
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid creature IDs: {invalid_ids}")
        
        return value


class JoinBattleRequestSerializer(serializers.Serializer):
    """Serializer dla dołączenia do walki"""
    battle_id = serializers.UUIDField()
    team_creatures = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=6
    )
    opponent_creatures = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=6,
        help_text="Lista ID creatures przeciwnika (pierwszy gracz)"
    )
    
    def validate(self, data):
        """Sprawdź czy battle istnieje i czy można do niego dołączyć"""
        try:
            battle = Battle.objects.get(id=data['battle_id'])
        except Battle.DoesNotExist:
            raise serializers.ValidationError("Battle not found")
        
        if battle.player2 is not None:
            raise serializers.ValidationError("Battle is already full")
        
        if battle.phase != 'waiting':
            raise serializers.ValidationError("Battle is not accepting new players")
        
        # Sprawdź czy gracz nie próbuje dołączyć do własnej walki
        user = self.context['request'].user
        if battle.player1.user == user:
            raise serializers.ValidationError("Cannot join your own battle")
        
        return data
    
    def validate_team_creatures(self, value):
        """Sprawdź czy wszystkie creatures należą do gracza"""
        user = self.context['request'].user
        try:
            player = user.player
        except:
            raise serializers.ValidationError("Player not found")
        
        player_creature_ids = set(player.creatures.values_list('id', flat=True))
        provided_creature_ids = set(value)
        
        invalid_ids = provided_creature_ids - player_creature_ids
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid creature IDs: {invalid_ids}")
        
        return value
from rest_framework import serializers
from .models import Game, PlayerData, Creature, CreatureSpell

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'slug', 'description', 'unity_build_url', 'is_active']

class CreatureSpellSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatureSpell
        fields = ['id', 'spell_id', 'start_time', 'end_time', 'is_learned']

class CreatureSerializer(serializers.ModelSerializer):
    spells = CreatureSpellSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Creature
        fields = [
            'id', 'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative', 'spells', 'owner_username'
        ]

class PlayerDataSerializer(serializers.ModelSerializer):
    """Pełny serializer dla PlayerData z creatures"""
    creatures = CreatureSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PlayerData
        fields = [
            'id', 'username', 'gold', 'wood', 'stone', 'gems', 'can_claim_start_creature',
            'creatures', 'last_played', 'created_at'
        ]
        read_only_fields = ['username', 'last_played', 'created_at']

class UpdateSingleResourceSerializer(serializers.Serializer):
    """Serializer dla aktualizacji pojedynczego zasobu"""
    RESOURCE_CHOICES = [
        ('gold', 'Gold'),
        ('wood', 'Wood'), 
        ('stone', 'Stone'),
        ('gems', 'Gems'),
    ]
    
    resource_type = serializers.ChoiceField(choices=RESOURCE_CHOICES)
    value = serializers.IntegerField(min_value=0)

class PlayerListSerializer(serializers.ModelSerializer):
    """Uproszczony serializer dla listy graczy"""
    username = serializers.CharField(source='user.username', read_only=True)
    creature_count = serializers.SerializerMethodField()
    
    def get_creature_count(self, obj):
        return obj.creatures.count()
    
    class Meta:
        model = PlayerData
        fields = ['username', 'gold', 'creature_count', 'last_played']

# Serializers dla operacji na creatures
class CreatureCreateSerializer(serializers.ModelSerializer):
    spells = serializers.ListField(
        child=serializers.DictField(), 
        required=False, 
        allow_empty=True,
        help_text="Lista spelli do dodania przy tworzeniu stworka"
    )
    
    class Meta:
        model = Creature
        fields = [
            'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative', 'spells'
        ]

class CreatureUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    
    class Meta:
        model = Creature
        fields = [
            'id', 'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative'
        ]

# Serializers dla operacji na spellach
class SpellLearnSerializer(serializers.ModelSerializer):
    """Serializer do rozpoczęcia nauki spella"""
    creature_id = serializers.IntegerField()
    
    class Meta:
        model = CreatureSpell
        fields = ['creature_id', 'spell_id', 'start_time', 'end_time']

class SpellCompleteSerializer(serializers.Serializer):
    """Serializer do oznaczenia spella jako nauczony"""
    creature_id = serializers.IntegerField()
    spell_id = serializers.IntegerField() 
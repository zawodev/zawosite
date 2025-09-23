from rest_framework import serializers
from .models import Player, Creature, Spell, City, Battle

class SpellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spell
        fields = ['spell_id', 'name', 'description', 'spell_img']

class CreatureSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)
    current_spell_name = serializers.SerializerMethodField()

    def get_current_spell_name(self, obj):
        if obj.learning_spell_id is not None:
            try:
                spell = Spell.objects.get(spell_id=obj.learning_spell_id)
                return spell.name
            except Spell.DoesNotExist:
                return None
        return None

    class Meta:
        model = Creature
        fields = [
            'id', 'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative', 'posX', 'posY', 'owner_username',
            'travel_from_x', 'travel_from_y', 'travel_to_x', 'travel_to_y',
            'travel_start_time', 'travel_end_time', 'travel_is_complete',
            'learning_spell_id', 'learning_start_time', 'learning_end_time',
            'learning_is_complete', 'current_spell_name'
        ]

class PlayerSerializer(serializers.ModelSerializer):
    """Pełny serializer dla Player z creatures i cities"""
    creatures = CreatureSerializer(many=True, read_only=True)
    cities = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    can_claim_creature = serializers.SerializerMethodField()

    def get_cities(self, obj):
        cities = City.objects.filter(owner=obj)
        return CitySerializer(cities, many=True).data

    def get_can_claim_creature(self, obj):
        if obj.last_creature_claim_time is None:
            return True
        # Można odebrać co 4 godziny
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > obj.last_creature_claim_time + timedelta(hours=4)

    class Meta:
        model = Player
        fields = [
            'id', 'username', 'gold', 'wood', 'stone', 'gems', 'experience',
            'can_claim_creature', 'creatures', 'cities', 'last_played', 'created_at'
        ]
        read_only_fields = ['username', 'last_played', 'created_at', 'can_claim_creature']

class UpdateSingleResourceSerializer(serializers.Serializer):
    """Serializer dla aktualizacji pojedynczego zasobu"""
    RESOURCE_CHOICES = [
        ('gold', 'Gold'),
        ('wood', 'Wood'),
        ('stone', 'Stone'),
        ('gems', 'Gems'),
        ('experience', 'Experience'),
    ]

    resource_type = serializers.ChoiceField(choices=RESOURCE_CHOICES)
    value = serializers.IntegerField(min_value=0)

class PlayerListSerializer(serializers.ModelSerializer):
    """Uproszczony serializer dla listy graczy"""
    username = serializers.CharField(source='user.username', read_only=True)
    creature_count = serializers.SerializerMethodField()
    city_count = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()

    def get_creature_count(self, obj):
        return obj.creatures.count()

    def get_city_count(self, obj):
        return obj.cities.count()

    def get_is_online(self, obj):
        # Gracz jest online jeśli był aktywny w ciągu ostatnich 5 minut
        from django.utils import timezone
        from datetime import timedelta
        threshold = timezone.now() - timedelta(minutes=5)
        return obj.last_played >= threshold

    class Meta:
        model = Player
        fields = ['username', 'experience', 'creature_count', 'city_count', 'is_online']

# Serializers dla operacji na creatures
class CreatureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creature
        fields = [
            'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative', 'posX', 'posY'
        ]

class CreatureUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Creature
        fields = [
            'id', 'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative', 'posX', 'posY'
        ]

# Serializers dla miast
class CitySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'description', 'posX', 'posY', 'owner_username']

class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'description', 'posX', 'posY']

# Serializers dla bitew
class BattleSerializer(serializers.ModelSerializer):
    player1_username = serializers.CharField(source='player1.user.username', read_only=True)
    player2_username = serializers.CharField(source='player2.user.username', read_only=True)

    class Meta:
        model = Battle
        fields = ['id', 'player1_username', 'player2_username', 'result', 'battle_data', 'created_at']

# Serializers dla operacji na spellach
class SpellLearnSerializer(serializers.ModelSerializer):
    """Serializer do rozpoczęcia nauki spella"""
    creature_id = serializers.IntegerField()

    class Meta:
        model = Creature
        fields = ['creature_id', 'learning_spell_id', 'learning_start_time', 'learning_end_time']

class SpellCompleteSerializer(serializers.Serializer):
    """Serializer do oznaczenia spella jako nauczonego"""
    creature_id = serializers.IntegerField()
    spell_id = serializers.IntegerField()
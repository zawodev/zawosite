from rest_framework import serializers
from .models import Player, Creature, Spell, City, CreatureSpell

class SpellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spell
        fields = ['spell_id', 'name', 'description', 'spell_img']

class CreatureSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)
    current_spell_name = serializers.SerializerMethodField()
    spells = serializers.SerializerMethodField()

    def get_current_spell_name(self, obj):
        if obj.learning_spell_id is not None:
            try:
                spell = Spell.objects.get(spell_id=obj.learning_spell_id)
                return spell.name
            except Spell.DoesNotExist:
                return None
        return None

    def get_spells(self, obj):
        """Zwraca listę poznanych spelli stworka w formacie oczekiwanym przez Unity"""
        spells_data = []
        for creature_spell in obj.known_spells.all():
            spells_data.append({
                'spell_id': creature_spell.spell.spell_id,
                'start_time': creature_spell.learned_at.isoformat(),
                'end_time': creature_spell.learned_at.isoformat(),  # Dla poznanych spelli start_time = end_time
                'is_learned': True
            })
        
        # Dodaj aktualnie uczący się spell (jeśli istnieje)
        if obj.learning_spell_id and not obj.learning_is_complete:
            spells_data.append({
                'spell_id': obj.learning_spell_id,
                'start_time': obj.learning_start_time.isoformat() if obj.learning_start_time else None,
                'end_time': obj.learning_end_time.isoformat() if obj.learning_end_time else None,
                'is_learned': False
            })
        
        return spells_data

    class Meta:
        model = Creature
        fields = [
            'id', 'name', 'main_element', 'secondary_element', 'color',
            'experience', 'max_hp', 'current_hp', 'max_energy', 'current_energy',
            'damage', 'initiative', 'posX', 'posY', 'owner_username',
            'travel_from_x', 'travel_from_y', 'travel_to_x', 'travel_to_y',
            'travel_start_time', 'travel_end_time', 'travel_is_complete',
            'learning_spell_id', 'learning_start_time', 'learning_end_time',
            'learning_is_complete', 'current_spell_name', 'spells'
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
        return obj.last_creature_claim_time is None or timezone.now() >= obj.last_creature_claim_time + timedelta(hours=4)

    class Meta:
        model = Player
        fields = [
            'id', 'username', 'gold', 'wood', 'stone', 'gems', 'experience',
            'can_claim_creature', 'creatures', 'cities', 'last_played', 'created_at'
        ]
        read_only_fields = ['username', 'last_played', 'created_at', 'can_claim_creature']

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

# Serializers dla miast
class CitySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'description', 'posX', 'posY', 'owner_username']
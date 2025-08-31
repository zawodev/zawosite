from django.db import models
from django.conf import settings
from django.utils import timezone

class Game(models.Model):
    """Model reprezentujący grę w systemie"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, default='default-game')  # np. 'zawomons'
    description = models.TextField(blank=True)
    unity_build_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.name

class PlayerData(models.Model):
    """Model przechowujący dane gracza dla konkretnej gry - odpowiednik PlayerData z Unity"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    # Dane gracza zgodne ze strukturą Unity PlayerData
    gold = models.IntegerField(default=100)
    wood = models.IntegerField(default=50)
    stone = models.IntegerField(default=25)
    gems = models.IntegerField(default=5)
    experience = models.IntegerField(default=0)  # Doświadczenie gracza
    can_claim_start_creature = models.BooleanField(default=True)  # Czy gracz może odebrać pierwszego stworka
    
    # Metadane Django
    last_played = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'game')
        indexes = [
            models.Index(fields=['user', 'game']),
            models.Index(fields=['last_played']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.game.name}"

class Creature(models.Model):
    """Model dla potworków gracza - odpowiednik Creature z Unity"""
    
    # Globalne unikalny ID i właściciel
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_creatures')
    # Powiązanie z PlayerData dla konkretnej gry (zostaje dla kompatybilności)
    player_data = models.ForeignKey(PlayerData, on_delete=models.CASCADE, related_name='creatures')
    
    # Dane creature zgodne ze strukturą Unity
    name = models.CharField(max_length=50)
    main_element = models.CharField(max_length=20)
    secondary_element = models.CharField(max_length=20, null=True, blank=True)
    
    # Kolory w Unity to Color - przechowamy jako hex string
    color = models.CharField(max_length=7, default="#FFFFFF")  # Format: #RRGGBB
    
    # Statystyki creature
    experience = models.IntegerField(default=0)
    max_hp = models.IntegerField(default=100)
    current_hp = models.IntegerField(default=100)
    max_energy = models.IntegerField(default=50)
    current_energy = models.IntegerField(default=50)
    damage = models.IntegerField(default=25)
    initiative = models.IntegerField(default=10)
    
    # Metadane Django
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.main_element}) - {self.player_data.user.username}"

class CreatureSpell(models.Model):
    """Model przechowujący spelle creature z informacjami o nauce"""
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, related_name='spells')
    spell_id = models.IntegerField()  # ID spella z Unity (statyczna lista)
    start_time = models.DateTimeField()  # Czas rozpoczęcia nauki (UTC)
    end_time = models.DateTimeField()    # Czas zakończenia nauki (UTC)
    is_learned = models.BooleanField(default=False)  # Czy spell został już nauczony
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        unique_together = ('creature', 'spell_id')
        indexes = [
            models.Index(fields=['creature', 'is_learned']),
            models.Index(fields=['end_time']),
        ]
    
    def __str__(self):
        status = "Learned" if self.is_learned else "Learning"
        return f"{self.creature.name} - Spell {self.spell_id} ({status})"

from django.db import models
from django.conf import settings
from django.utils import timezone

class Player(models.Model):
    """Model przechowujący dane gracza w grze zawomons"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # zasoby gracza
    gold = models.IntegerField(default=100)
    wood = models.IntegerField(default=50)
    stone = models.IntegerField(default=25)
    gems = models.IntegerField(default=5)

    # doświadczenie gracza
    experience = models.IntegerField(default=0)

    # flagi specjalne
    can_claim_start_creature = models.BooleanField(default=True)

    # metadane django
    last_played = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"

class Creature(models.Model):
    """Model dla stworków gracza w grze zawomons"""
    # właściciel (może być null dla dzikich stworków)
    owner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='creatures')

    # podstawowe dane stworka
    name = models.CharField(max_length=50)
    main_element = models.CharField(max_length=20)
    secondary_element = models.CharField(max_length=20, null=True, blank=True)

    # color - przechowamy jako hex string
    color = models.CharField(max_length=7, default="#FFFFFF")  # format: #RRGGBB

    # statystyki stworka
    experience = models.IntegerField(default=0)
    max_hp = models.IntegerField(default=100)
    current_hp = models.IntegerField(default=100)
    max_energy = models.IntegerField(default=50)
    current_energy = models.IntegerField(default=50)
    damage = models.IntegerField(default=25)
    initiative = models.IntegerField(default=10)

    # pozycja na mapie
    posX = models.FloatField(default=0.0)
    posY = models.FloatField(default=0.0)

    # informacje o podróży
    travel_from_x = models.FloatField(null=True, blank=True)
    travel_from_y = models.FloatField(null=True, blank=True)
    travel_to_x = models.FloatField(null=True, blank=True)
    travel_to_y = models.FloatField(null=True, blank=True)
    travel_start_time = models.DateTimeField(null=True, blank=True)
    travel_end_time = models.DateTimeField(null=True, blank=True)
    travel_is_complete = models.BooleanField(default=False)

    # informacje o nauce spella
    learning_spell_id = models.IntegerField(null=True, blank=True)
    learning_start_time = models.DateTimeField(null=True, blank=True)
    learning_end_time = models.DateTimeField(null=True, blank=True)
    learning_is_complete = models.BooleanField(default=False)

    # metadane django
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.owner.user.username if self.owner else 'Wild'})"

class Spell(models.Model):
    """Statyczna lista spelli dostępnych w grze"""
    spell_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    spell_img = models.URLField(blank=True, null=True)  # url do obrazka spella

    def __str__(self):
        return f"{self.name} (ID: {self.spell_id})"

class City(models.Model):
    """Model dla miast w grze Zawomons"""

    # pozycja na mapie
    posX = models.FloatField()
    posY = models.FloatField()

    # właściciel (może być null dla neutralnych miast)
    owner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='cities')

    # dane miasta
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # metadane django
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.owner.user.username if self.owner else 'Neutral'}"

class Battle(models.Model):
    """Model dla bitew między graczami"""

    # uczestnicy bitwy
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='battles_as_player1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='battles_as_player2')

    # wynik bitwy
    RESULT_CHOICES = [
        ('player1_win', 'Player 1 Wins'),
        ('player2_win', 'Player 2 Wins'),
        ('draw', 'Draw'),
        ('ongoing', 'Ongoing'),
    ]
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='ongoing')

    # szczegóły bitwy (można rozszerzyć)
    battle_data = models.JSONField(null=True, blank=True)  # JSON z detalami bitwy

    # metadane django
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Battle: {self.player1.user.username} vs {self.player2.user.username} - {self.result}"

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

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
    last_creature_claim_time = models.DateTimeField(null=True, blank=True)  # kiedy ostatnio odebrano darmowego stworka

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
    color = models.CharField(max_length=7, default="#FF00DD")  # format: #RRGGBB

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

class CreatureSpell(models.Model):
    """Model dla relacji many-to-many między Creature a Spell - poznane spelle"""
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, related_name='known_spells')
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    learned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('creature', 'spell')  # jeden stworek nie może mieć tego samego spella dwa razy

    def __str__(self):
        return f"{self.creature.name} knows {self.spell.name}"

class City(models.Model):
    """Model dla miast w grze zawomons"""

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

### Battle Models for WebSocket battles

class Battle(models.Model):
    """Model reprezentujący walkę między dwoma graczami"""
    
    BATTLE_TYPES = [
        ('friendly', 'Friendly Match'),  # sparring - brak konsekwencji
        ('ranked', 'Ranked Battle'),    # pełna walka - zmiana HP, exp
    ]
    
    BATTLE_PHASES = [
        ('waiting', 'Waiting for players'),
        ('selection', 'Move selection'),
        ('combat', 'Combat execution'),
        ('finished', 'Battle finished'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    battle_type = models.CharField(max_length=10, choices=BATTLE_TYPES, default='friendly')
    phase = models.CharField(max_length=10, choices=BATTLE_PHASES, default='waiting')
    
    # gracze
    player1 = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='websocket_battles_as_player1')
    player2 = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='websocket_battles_as_player2', null=True, blank=True)
    
    # wynik
    winner = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='websocket_won_battles')
    
    current_turn = models.IntegerField(default=0)
    
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Battle {self.id} - {self.player1} vs {self.player2 or 'waiting'}"


class BattleParticipant(models.Model):
    """Model reprezentujący uczestnika walki (creature w battle)"""
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='participants')
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    creature = models.ForeignKey('Creature', on_delete=models.CASCADE)
    
    # stan w walce
    current_hp = models.IntegerField()
    current_energy = models.IntegerField()
    initiative_bonus = models.IntegerField(default=0)
    
    # wybory ruchu
    selected_spell = models.ForeignKey('Spell', on_delete=models.SET_NULL, null=True, blank=True)
    selected_target = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    has_confirmed_move = models.BooleanField(default=False)
    
    # pozycja w teamie (1 lub 2)
    team = models.IntegerField()  # 1 = team A, 2 = team B
    
    def reset_move_selection(self):
        """Reset wyboru ruchu na następną turę"""
        self.selected_spell = None
        self.selected_target = None
        self.has_confirmed_move = False
        self.save()
    
    @property
    def is_alive(self):
        return self.current_hp > 0
    
    @property
    def total_initiative(self):
        return self.creature.initiative + self.initiative_bonus
    
    def __str__(self):
        return f"{self.creature.name} (Team {self.team}) - {self.current_hp}/{self.creature.max_hp}HP"


class BattleAction(models.Model):
    """Model przechowujący akcje wykonane w walce (do historii i animacji)"""
    
    ACTION_TYPES = [
        ('spell_cast', 'Spell Cast'),
        ('damage_dealt', 'Damage Dealt'),
        ('heal_performed', 'Heal Performed'),
        ('buff_applied', 'Buff Applied'),
    ]
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='actions')
    turn_number = models.IntegerField()
    action_order = models.IntegerField()  # kolejność w turze
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    caster = models.ForeignKey(BattleParticipant, on_delete=models.CASCADE, related_name='actions_performed')
    target = models.ForeignKey(BattleParticipant, on_delete=models.CASCADE, related_name='actions_received', null=True, blank=True)
    spell_used = models.ForeignKey('Spell', on_delete=models.CASCADE, null=True, blank=True)
    
    # efekt akcji
    damage_amount = models.IntegerField(default=0)
    heal_amount = models.IntegerField(default=0)
    initiative_bonus = models.IntegerField(default=0)
    damage_bonus = models.IntegerField(default=0)
    
    # stan po akcji
    target_hp_after = models.IntegerField(null=True, blank=True)
    target_alive_after = models.BooleanField(default=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"T{self.turn_number}.{self.action_order}: {self.caster.creature.name} -> {self.action_type}"

class GameInvitation(models.Model):
    """Model zaproszenia do gry"""
    
    INVITATION_TYPES = [
        ('friendly', 'Friendly Battle'),
        ('ranked', 'Ranked Battle'),
    ]
    
    INVITATION_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # gracze
    sender = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='received_invitations')
    
    # typ zaproszenia
    invitation_type = models.CharField(max_length=10, choices=INVITATION_TYPES, default='friendly')
    status = models.CharField(max_length=10, choices=INVITATION_STATUS, default='pending')
    
    # creatures wybrane przez sender
    sender_creatures = models.JSONField(default=list, help_text="Lista ID creatures wybranych przez wysyłającego")
    
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # zaproszenia wygasają po 2 minutach
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # powiązana walka (gdy zaproszenie zostanie zaakceptowane)
    battle = models.ForeignKey('Battle', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Zaproszenia wygasają po 2 minutach
            self.expires_at = timezone.now() + timezone.timedelta(minutes=2)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def can_respond(self):
        return self.status == 'pending' and not self.is_expired()
    
    def __str__(self):
        return f"Invitation {self.id}: {self.sender.user.username} -> {self.receiver.user.username} ({self.status})"

### IN FUTURE:
# - add biomes data
# - add maps data
# - add worlds data?
# - add items? for ekwipunek
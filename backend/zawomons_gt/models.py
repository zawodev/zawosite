from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GameMode(models.TextChoices):
    CLASSIC_1V1 = 'classic_1v1', 'Classic 1v1'
    TOURNAMENT = 'tournament', 'Tournament'
    BOSS_FIGHT = 'boss_fight', 'Boss Fight'


class LobbyStatus(models.TextChoices):
    WAITING = 'waiting', 'Waiting'
    IN_PROGRESS = 'in_progress', 'In Progress'
    FINISHED = 'finished', 'Finished'


class Lobby(models.Model):
    code = models.CharField(max_length=8, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_gt_lobbies')
    game_mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.CLASSIC_1V1)
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=LobbyStatus.choices, default=LobbyStatus.WAITING)
    max_players = models.IntegerField(default=2)
    
    # Game settings
    round_duration = models.IntegerField(default=60, help_text='Round duration in seconds')
    cards_per_turn = models.IntegerField(default=5, help_text='Cards drawn per turn')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Lobbies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def current_players_count(self):
        return self.players.count()

    @property
    def is_full(self):
        return self.current_players_count >= self.max_players

    @property
    def can_start(self):
        if self.game_mode == GameMode.CLASSIC_1V1:
            return self.current_players_count == 2
        elif self.game_mode == GameMode.TOURNAMENT:
            return self.current_players_count >= 4
        elif self.game_mode == GameMode.BOSS_FIGHT:
            return self.current_players_count >= 2
        return False


class LobbyPlayer(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gt_lobby_participations', null=True, blank=True)
    guest_username = models.CharField(max_length=50, null=True, blank=True)
    is_ready = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['lobby', 'user'], ['lobby', 'guest_username']]
        ordering = ['joined_at']

    def __str__(self):
        username = self.user.username if self.user else self.guest_username
        return f"{username} in {self.lobby.code}"

    @property
    def display_name(self):
        return self.user.username if self.user else self.guest_username

    @property
    def avatar_url(self):
        if self.user and hasattr(self.user, 'avatar'):
            return self.user.avatar.url if self.user.avatar else None
        return None

from django.db import models
from django.conf import settings

class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unity_build_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class GameSave(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_saves')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='saves')
    save_data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} - {self.game.name}"

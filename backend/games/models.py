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

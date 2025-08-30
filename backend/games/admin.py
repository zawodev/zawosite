from django.contrib import admin
from .models import Game, PlayerData, Creature

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')

@admin.register(PlayerData)
class PlayerDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'gold', 'wood', 'stone', 'gems', 'last_played')
    list_filter = ('game', 'last_played', 'created_at')
    search_fields = ('user__username',)

@admin.register(Creature)
class CreatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'player_data', 'main_element', 'secondary_element', 'experience', 'current_hp')
    list_filter = ('main_element', 'secondary_element', 'created_at')
    search_fields = ('name', 'owner__username', 'player_data__user__username')

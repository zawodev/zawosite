from django.contrib import admin
from .models import Lobby, LobbyPlayer


@admin.register(Lobby)
class LobbyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'host', 'game_mode', 'status', 'current_players_count', 'max_players', 'created_at']
    list_filter = ['game_mode', 'status', 'is_public']
    search_fields = ['code', 'name', 'host__username']
    readonly_fields = ['code', 'created_at', 'updated_at']


@admin.register(LobbyPlayer)
class LobbyPlayerAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'lobby', 'is_ready', 'joined_at']
    list_filter = ['is_ready', 'joined_at']
    search_fields = ['user__username', 'guest_username', 'lobby__code']

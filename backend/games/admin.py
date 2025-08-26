from django.contrib import admin
from .models import Game, PlayerData, Creature, CreatureSpell, CreatureLearningSpell

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
    list_display = ('name', 'player_data', 'main_element', 'secondary_element', 'experience', 'current_hp')
    list_filter = ('main_element', 'secondary_element', 'created_at')
    search_fields = ('name', 'player_data__user__username')

@admin.register(CreatureSpell)
class CreatureSpellAdmin(admin.ModelAdmin):
    list_display = ('creature', 'spell_id', 'learned_at')
    list_filter = ('learned_at',)
    search_fields = ('creature__name',)

@admin.register(CreatureLearningSpell)
class CreatureLearningSpellAdmin(admin.ModelAdmin):
    list_display = ('creature', 'spell_id', 'start_time_utc', 'end_time_utc', 'is_completed')
    list_filter = ('is_completed', 'start_time_utc', 'end_time_utc')
    search_fields = ('creature__name',)

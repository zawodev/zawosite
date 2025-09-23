from django.contrib import admin
from .models import PlayerData, Creature, CreatureSpell

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
    list_display = ('creature', 'spell_id', 'start_time', 'end_time', 'is_learned')
    list_filter = ('is_learned', 'start_time', 'end_time')
    search_fields = ('creature__name',)

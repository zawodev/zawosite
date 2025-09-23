from django.contrib import admin
from .models import Player, Creature, Spell, City, Battle

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'gold', 'wood', 'stone', 'gems', 'experience', 'last_creature_claim_time', 'last_played')
    list_filter = ('last_played', 'created_at')
    search_fields = ('user__username',)

@admin.register(Creature)
class CreatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'main_element', 'secondary_element', 'experience', 'current_hp', 'posX', 'posY')
    list_filter = ('main_element', 'secondary_element', 'created_at')
    search_fields = ('name', 'owner__user__username')

@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    list_display = ('spell_id', 'name', 'description')
    search_fields = ('name', 'spell_id')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'posX', 'posY')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__user__username')

@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'result', 'created_at')
    list_filter = ('result', 'created_at')
    search_fields = ('player1__user__username', 'player2__user__username')

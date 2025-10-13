from django.contrib import admin
from .models import Player, Creature, Spell, City, Battle, BattleParticipant, BattleAction, GameInvitation

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
    list_display = ('id', 'player1', 'player2', 'battle_type', 'phase', 'winner', 'created_at')
    list_filter = ('battle_type', 'phase', 'created_at')
    search_fields = ('player1__user__username', 'player2__user__username')
    readonly_fields = ('id', 'created_at', 'started_at', 'finished_at')

@admin.register(BattleParticipant)
class BattleParticipantAdmin(admin.ModelAdmin):
    list_display = ('creature', 'player', 'battle', 'team', 'current_hp', 'is_alive')
    list_filter = ('team', 'battle__battle_type')
    search_fields = ('creature__name', 'player__user__username')

@admin.register(BattleAction)
class BattleActionAdmin(admin.ModelAdmin):
    list_display = ('battle', 'turn_number', 'action_order', 'action_type', 'caster', 'target')
    list_filter = ('action_type', 'battle__battle_type')
    search_fields = ('caster__creature__name', 'target__creature__name')

@admin.register(GameInvitation)
class GameInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'invitation_type', 'status', 'created_at', 'expires_at')
    list_filter = ('invitation_type', 'status', 'created_at')
    search_fields = ('sender__user__username', 'receiver__user__username')
    readonly_fields = ('id', 'created_at', 'expires_at', 'responded_at')

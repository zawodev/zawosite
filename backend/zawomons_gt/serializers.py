from rest_framework import serializers
from .models import Lobby, LobbyPlayer, GameMode


class LobbyPlayerSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = LobbyPlayer
        fields = ['id', 'display_name', 'avatar_url', 'is_ready', 'joined_at']


class LobbySerializer(serializers.ModelSerializer):
    players = LobbyPlayerSerializer(many=True, read_only=True)
    current_players_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    can_start = serializers.BooleanField(read_only=True)
    host_username = serializers.SerializerMethodField()
    
    def get_host_username(self, obj):
        # For guest-created lobbies, return the first player's name
        if obj.host:
            return obj.host.username
        first_player = obj.players.order_by('id').first()
        if first_player:
            return first_player.display_name
        return "Unknown"
    
    class Meta:
        model = Lobby
        fields = [
            'id', 'code', 'name', 'host_username', 'game_mode', 'is_public',
            'status', 'max_players', 'current_players_count', 'is_full',
            'can_start', 'players', 'created_at', 'started_at'
        ]
        read_only_fields = ['code', 'host_username', 'status', 'created_at', 'started_at']


class CreateLobbySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    game_mode = serializers.ChoiceField(choices=GameMode.choices, default=GameMode.CLASSIC_1V1)
    is_public = serializers.BooleanField(default=True)
    max_players = serializers.IntegerField(default=2, min_value=2, max_value=16)


class JoinLobbySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)
    guest_username = serializers.CharField(max_length=50, required=False, allow_blank=True)

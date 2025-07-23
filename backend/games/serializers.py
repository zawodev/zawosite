from rest_framework import serializers
from .models import Game, GameSave

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'description', 'unity_build_url']

class GameSaveSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    game_id = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), source='game', write_only=True)

    class Meta:
        model = GameSave
        fields = ['id', 'user', 'game', 'game_id', 'save_data', 'updated_at']
        read_only_fields = ['user', 'game', 'updated_at'] 
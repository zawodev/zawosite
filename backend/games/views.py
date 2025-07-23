from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Game, GameSave
from .serializers import GameSerializer, GameSaveSerializer
from users.models import User
from drf_spectacular.utils import extend_schema

# Create your views here.

@extend_schema(responses=GameSerializer)
class GameList(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(responses=GameSerializer)
class GameDetail(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(responses=GameSaveSerializer)
class GameSaveListCreate(generics.ListCreateAPIView):
    serializer_class = GameSaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GameSave.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(responses=GameSaveSerializer)
class GameSaveDetail(generics.RetrieveUpdateAPIView):
    serializer_class = GameSaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GameSave.objects.filter(user=self.request.user)

@extend_schema(responses=GameSaveSerializer)
class GameSaveForUser(generics.ListAPIView):
    serializer_class = GameSaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return GameSave.objects.filter(user__id=user_id)

@extend_schema(responses=GameSaveSerializer)
class GameSaveForFriends(generics.ListAPIView):
    serializer_class = GameSaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        friends = self.request.user.friends.all()
        return GameSave.objects.filter(user__in=friends)

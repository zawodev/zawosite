from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game
from .serializers import GameSerializer
from users.models import User
from drf_spectacular.utils import extend_schema

# Create your views here.

@extend_schema(responses=GameSerializer)
class GameList(generics.ListAPIView):
    """Lista dostępnych gier"""
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]

from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game, PlayerData, Creature
from .serializers import (GameSerializer, PlayerDataSerializer, 
                         PlayerListSerializer, UpdateSingleResourceSerializer,
                         CreatureSerializer, CreatureCreateSerializer, 
                         CreatureUpdateSerializer)
from users.models import User
from drf_spectacular.utils import extend_schema

# Create your views here.

@extend_schema(responses=GameSerializer)
class GameList(generics.ListAPIView):
    """Lista dostępnych gier"""
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]

# Views specyficzne dla gry Zawomons
class ZawomonsPlayerDataGetView(APIView):
    """GET: Pobierz dane gracza dla gry Zawomons"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=PlayerDataSerializer)
    def get(self, request):
        try:
            game = get_object_or_404(Game, slug='zawomons')
            player_data, created = PlayerData.objects.get_or_create(
                user=request.user,
                game=game,
                defaults={
                    'gold': 100,  # Początkowe wartości
                    'wood': 50,
                    'stone': 25,
                    'gems': 5,
                    'can_claim_start_creature': True,  # Nowi gracze mogą odebrać pierwszego stworka
                }
            )
            
            serializer = PlayerDataSerializer(player_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayersListView(APIView):
    """GET: Lista wszystkich graczy gry Zawomons"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=PlayerListSerializer(many=True))
    def get(self, request):
        try:
            game = get_object_or_404(Game, slug='zawomons')
            players = PlayerData.objects.filter(game=game).order_by('-gold')
            
            serializer = PlayerListSerializer(players, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsSetSingleResourceView(APIView):
    """POST: Zaktualizuj pojedynczy zasób gracza dla gry Zawomons"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(request=UpdateSingleResourceSerializer, responses=PlayerDataSerializer)
    def post(self, request):
        try:
            game = get_object_or_404(Game, slug='zawomons')
            player_data, created = PlayerData.objects.get_or_create(
                user=request.user,
                game=game,
                defaults={
                    'gold': 100,
                    'wood': 50,
                    'stone': 25,
                    'gems': 5,
                    'can_claim_start_creature': True,
                }
            )
            
            # Walidacja danych wejściowych
            serializer = UpdateSingleResourceSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            resource_type = serializer.validated_data['resource_type']
            value = serializer.validated_data['value']
            
            # Aktualizacja odpowiedniego zasobu
            if resource_type == 'gold':
                player_data.gold = value
            elif resource_type == 'wood':
                player_data.wood = value
            elif resource_type == 'stone':
                player_data.stone = value
            elif resource_type == 'gems':
                player_data.gems = value
            
            player_data.save()
            
            # Zwróć pełne dane gracza
            full_serializer = PlayerDataSerializer(player_data)
            return Response(full_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Views for Creature management
class ZawomonsCreatureGetView(APIView):
    """GET: Pobierz szczegóły konkretnego stworka"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=CreatureSerializer)
    def get(self, request, creature_id):
        try:
            creature = get_object_or_404(Creature, id=creature_id)
            
            # Sprawdź czy użytkownik ma dostęp do tego stworka (jest właścicielem)
            if creature.owner != request.user:
                return Response({'error': 'Nie masz dostępu do tego stworka'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            creature_serializer = CreatureSerializer(creature)
            return Response(creature_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsCreatureAddView(APIView):
    """POST: Stwórz nowego stworka"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(request=CreatureCreateSerializer, responses=CreatureSerializer)
    def post(self, request):
        try:
            game = get_object_or_404(Game, slug='zawomons')
            player_data, created = PlayerData.objects.get_or_create(
                user=request.user,
                game=game,
                defaults={
                    'gold': 100,
                    'wood': 50,
                    'stone': 25,
                    'gems': 5,
                    'can_claim_start_creature': True,
                }
            )
            
            serializer = CreatureCreateSerializer(data=request.data)
            if serializer.is_valid():
                # Stwórz nowego stworka z automatycznym ustawieniem właściciela
                creature = serializer.save(
                    owner=request.user,
                    player_data=player_data
                )
                
                # Wyłącz flagę can_claim_start_creature po dodaniu stworka
                player_data.can_claim_start_creature = False
                player_data.save()
                
                # Zwróć szczegóły stworzonego stworka
                response_serializer = CreatureSerializer(creature)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsCreatureSetView(APIView):
    """POST: Zaktualizuj istniejącego stworka"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(request=CreatureUpdateSerializer, responses=CreatureSerializer)
    def post(self, request):
        try:
            creature_id = request.data.get('id')
            if not creature_id:
                return Response({'error': 'Musisz podać ID stworka'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            creature = get_object_or_404(Creature, id=creature_id)
            
            # Sprawdź czy użytkownik jest właścicielem
            if creature.owner != request.user:
                return Response({'error': 'Nie możesz edytować tego stworka - nie jesteś jego właścicielem'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            serializer = CreatureUpdateSerializer(creature, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Zwróć zaktualizowane dane stworka
                response_serializer = CreatureSerializer(creature)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

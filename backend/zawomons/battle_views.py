from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Battle, BattleParticipant, Player
from .battle_serializers import (
    BattleSerializer, 
    CreateBattleRequestSerializer, 
    JoinBattleRequestSerializer,
    BattleParticipantSerializer
)
from .battle_engine import BattleMatchmaker
from drf_spectacular.utils import extend_schema


class CreateBattleView(APIView):
    """Tworzy nową walkę dla gracza"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=CreateBattleRequestSerializer,
        responses={201: BattleSerializer}
    )
    def post(self, request):
        try:
            # Pobierz gracza
            player = get_object_or_404(Player, user=request.user)
            
            # Waliduj dane
            serializer = CreateBattleRequestSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Utwórz walkę
            battle_type = serializer.validated_data['battle_type']
            battle = BattleMatchmaker.create_battle(player, battle_type)
            
            # Zwróć dane walki
            battle_serializer = BattleSerializer(battle)
            return Response({
                'battle': battle_serializer.data,
                'message': f'{battle_type.capitalize()} battle created. Waiting for opponent.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JoinBattleView(APIView):
    """Dołącza gracza do istniejącej walki"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=JoinBattleRequestSerializer,
        responses={200: BattleSerializer}
    )
    def post(self, request):
        try:
            # Pobierz gracza
            player = get_object_or_404(Player, user=request.user)
            
            # Waliduj dane
            serializer = JoinBattleRequestSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Pobierz walkę
            battle = get_object_or_404(Battle, id=serializer.validated_data['battle_id'])
            
            # Dołącz do walki
            team_creatures = serializer.validated_data['team_creatures']
            opponent_creatures = serializer.validated_data['opponent_creatures']
            
            success = BattleMatchmaker.join_battle(battle, player, opponent_creatures, team_creatures)
            
            if not success:
                return Response({'error': 'Failed to join battle'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Zwróć dane walki z uczestnikami
            battle_serializer = BattleSerializer(battle)
            participants = BattleParticipant.objects.filter(battle=battle)
            participants_serializer = BattleParticipantSerializer(participants, many=True)
            
            return Response({
                'battle': battle_serializer.data,
                'participants': participants_serializer.data,
                'message': 'Successfully joined battle!'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BattleListView(APIView):
    """Lista walk gracza"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=BattleSerializer(many=True))
    def get(self, request):
        try:
            # Pobierz gracza
            player = get_object_or_404(Player, user=request.user)
            
            # Pobierz walki gracza
            battles = Battle.objects.filter(
                models.Q(player1=player) | models.Q(player2=player)
            ).order_by('-created_at')[:20]  # ostatnie 20 walk
            
            serializer = BattleSerializer(battles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BattleDetailView(APIView):
    """Szczegóły konkretnej walki"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=BattleSerializer)
    def get(self, request, battle_id):
        try:
            # Pobierz gracza
            player = get_object_or_404(Player, user=request.user)
            
            # Pobierz walkę (tylko te w których gracz uczestniczy)
            battle = Battle.objects.filter(
                id=battle_id
            ).filter(
                models.Q(player1=player) | models.Q(player2=player)
            ).first()
            
            if not battle:
                return Response({'error': 'Battle not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Serializuj walkę z uczestnikami
            battle_serializer = BattleSerializer(battle)
            participants = BattleParticipant.objects.filter(battle=battle)
            participants_serializer = BattleParticipantSerializer(participants, many=True)
            
            return Response({
                'battle': battle_serializer.data,
                'participants': participants_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OpenBattlesView(APIView):
    """Lista otwartych walk oczekujących na graczy"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=BattleSerializer(many=True))
    def get(self, request):
        try:
            # Pobierz walki czekające na gracza (ale nie własne)
            battles = Battle.objects.filter(
                phase='waiting',
                player2__isnull=True
            ).exclude(
                player1__user=request.user
            ).order_by('-created_at')[:10]  # 10 najnowszych
            
            serializer = BattleSerializer(battles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
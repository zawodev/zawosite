from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import Lobby, LobbyPlayer, GameMode, LobbyStatus
from .serializers import (
    LobbySerializer, CreateLobbySerializer, 
    JoinLobbySerializer, LobbyPlayerSerializer
)


class LobbyViewSet(viewsets.ModelViewSet):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer
    permission_classes = [AllowAny]
    lookup_field = 'code'

    def get_queryset(self):
        queryset = Lobby.objects.all()
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by game mode
        game_mode = self.request.query_params.get('game_mode', None)
        if game_mode:
            queryset = queryset.filter(game_mode=game_mode)
        
        # Only public lobbies for listing (unless user is host or player)
        if self.action == 'list':
            queryset = queryset.filter(is_public=True, status=LobbyStatus.WAITING)
        
        return queryset

    @action(detail=False, methods=['post'])
    def create_lobby(self, request):
        serializer = CreateLobbySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique code
        code = get_random_string(6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        while Lobby.objects.filter(code=code).exists():
            code = get_random_string(6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        # Determine host (authenticated user or None for guest)
        host = request.user if request.user.is_authenticated else None
        guest_username = request.data.get('guest_username', None)

        if not host and not guest_username:
            return Response(
                {'error': 'Guest must provide username'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # For guests, create a temporary user or handle differently
        if not host:
            # For now, guests cannot create lobbies
            return Response(
                {'error': 'Only authenticated users can create lobbies'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Create lobby
        lobby = Lobby.objects.create(
            code=code,
            host=host,
            **serializer.validated_data
        )

        # Add host as first player
        LobbyPlayer.objects.create(
            lobby=lobby,
            user=host,
            is_ready=True
        )

        return Response(
            LobbySerializer(lobby).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def join(self, request, code=None):
        try:
            lobby = Lobby.objects.get(code=code)
        except Lobby.DoesNotExist:
            return Response(
                {'error': 'Lobby not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if lobby.status != LobbyStatus.WAITING:
            return Response(
                {'error': 'Lobby already started or finished'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if lobby.is_full:
            return Response(
                {'error': 'Lobby is full'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user if request.user.is_authenticated else None
        guest_username = request.data.get('guest_username', None)

        if not user and not guest_username:
            return Response(
                {'error': 'Guest must provide username'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already in lobby
        if user:
            if LobbyPlayer.objects.filter(lobby=lobby, user=user).exists():
                return Response(
                    {'error': 'Already in this lobby'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if LobbyPlayer.objects.filter(lobby=lobby, guest_username=guest_username).exists():
                return Response(
                    {'error': 'Username already taken in this lobby'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Add player
        LobbyPlayer.objects.create(
            lobby=lobby,
            user=user,
            guest_username=guest_username if not user else None
        )

        return Response(
            LobbySerializer(lobby).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def leave(self, request, code=None):
        try:
            lobby = Lobby.objects.get(code=code)
        except Lobby.DoesNotExist:
            return Response(
                {'error': 'Lobby not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user if request.user.is_authenticated else None
        guest_username = request.data.get('guest_username', None)

        if user:
            player = LobbyPlayer.objects.filter(lobby=lobby, user=user).first()
        else:
            player = LobbyPlayer.objects.filter(lobby=lobby, guest_username=guest_username).first()

        if not player:
            return Response(
                {'error': 'Not in this lobby'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If host leaves, delete lobby or transfer ownership
        if user and lobby.host == user:
            # For now, delete the lobby
            lobby.delete()
            return Response({'message': 'Lobby deleted'}, status=status.HTTP_200_OK)
        
        player.delete()
        return Response({'message': 'Left lobby'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def start(self, request, code=None):
        try:
            lobby = Lobby.objects.get(code=code)
        except Lobby.DoesNotExist:
            return Response(
                {'error': 'Lobby not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user if request.user.is_authenticated else None
        
        # Only host can start
        if not user or lobby.host != user:
            return Response(
                {'error': 'Only host can start the game'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not lobby.can_start:
            return Response(
                {'error': 'Not enough players to start'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lobby.status = LobbyStatus.IN_PROGRESS
        lobby.started_at = timezone.now()
        lobby.save()

        return Response(
            LobbySerializer(lobby).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def update_settings(self, request, code=None):
        try:
            lobby = Lobby.objects.get(code=code)
        except Lobby.DoesNotExist:
            return Response(
                {'error': 'Lobby not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user if request.user.is_authenticated else None
        
        # Only host can update settings
        if not user or lobby.host != user:
            return Response(
                {'error': 'Only host can update settings'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update allowed fields
        allowed_fields = ['round_duration', 'cards_per_turn', 'is_public']
        for field in allowed_fields:
            if field in request.data:
                setattr(lobby, field, request.data[field])
        
        lobby.save()

        return Response(
            LobbySerializer(lobby).data,
            status=status.HTTP_200_OK
        )

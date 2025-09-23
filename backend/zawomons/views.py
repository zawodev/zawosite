from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Player, Creature, Spell, City, Battle
from .serializers import (PlayerSerializer,
                         PlayerListSerializer, UpdateSingleResourceSerializer,
                         CreatureSerializer, CreatureCreateSerializer,
                         CreatureUpdateSerializer, SpellLearnSerializer,
                         SpellCompleteSerializer, SpellSerializer,
                         CitySerializer, CityCreateSerializer, BattleSerializer)
from users.models import User
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta

# Create your views here.

# Views specyficzne dla gry Zawomons
class ZawomonsPlayerDataGetView(APIView):
    """GET: Pobierz dane gracza dla gry Zawomons"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=PlayerSerializer)
    def get(self, request):
        try:
            player, created = Player.objects.get_or_create(
                user=request.user,
                defaults={
                    'gold': 100,  # Początkowe wartości
                    'wood': 50,
                    'stone': 25,
                    'gems': 5,
                }
            )

            serializer = PlayerSerializer(player)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayersListView(APIView):
    """GET: Lista wszystkich graczy gry Zawomons"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=PlayerListSerializer(many=True))
    def get(self, request):
        try:
            players = Player.objects.all().order_by('-experience')

            serializer = PlayerListSerializer(players, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsFriendsListView(APIView):
    """GET: Lista znajomych gracza w grze Zawomons"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=PlayerListSerializer(many=True))
    def get(self, request):
        try:
            # Pobierz IDs znajomych aktualnego użytkownika
            friend_ids = request.user.friends.values_list('id', flat=True)

            # Pobierz Player znajomych
            friends_player_data = Player.objects.filter(
                user_id__in=friend_ids
            ).order_by('-experience')

            serializer = PlayerListSerializer(friends_player_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsSetSingleResourceView(APIView):
    """POST: Zaktualizuj pojedynczy zasób gracza dla gry Zawomons"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=UpdateSingleResourceSerializer, responses=PlayerSerializer)
    def post(self, request):
        try:
            player, created = Player.objects.get_or_create(
                user=request.user,
                defaults={
                    'gold': 100,
                    'wood': 50,
                    'stone': 25,
                    'gems': 5,
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
                player.gold = value
            elif resource_type == 'wood':
                player.wood = value
            elif resource_type == 'stone':
                player.stone = value
            elif resource_type == 'gems':
                player.gems = value
            elif resource_type == 'experience':
                player.experience = value

            player.save()

            # Zwróć pełne dane gracza
            full_serializer = PlayerSerializer(player)
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
            if creature.owner != request.user.player:
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
            player, created = Player.objects.get_or_create(
                user=request.user,
                defaults={
                    'gold': 100,
                    'wood': 50,
                    'stone': 25,
                    'gems': 5,
                }
            )

            # Sprawdź czy gracz może odebrać stworka (co 4 godziny)
            if player.last_creature_claim_time and timezone.now() < player.last_creature_claim_time + timedelta(hours=4):
                return Response({'error': 'Możesz odebrać nowego stworka tylko raz na 4 godziny'},
                              status=status.HTTP_400_BAD_REQUEST)

            serializer = CreatureCreateSerializer(data=request.data)
            if serializer.is_valid():
                creature = serializer.save(owner=player)

                # Zaktualizuj czas ostatniego odbioru stworka
                player.last_creature_claim_time = timezone.now()
                player.save()

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
            if creature.owner != request.user.player:
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

# Views for Spell management
class ZawomonsSpellLearnView(APIView):
    """POST: Rozpocznij naukę nowego spella dla creature"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=SpellLearnSerializer, responses=CreatureSerializer)
    def post(self, request):
        try:
            serializer = SpellLearnSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            creature_id = serializer.validated_data['creature_id']
            creature = get_object_or_404(Creature, id=creature_id)

            # Sprawdź czy użytkownik jest właścicielem creature
            if creature.owner != request.user.player:
                return Response({'error': 'Nie masz dostępu do tego stworka'},
                              status=status.HTTP_403_FORBIDDEN)

            # Sprawdź czy spell istnieje
            spell_id = serializer.validated_data['learning_spell_id']
            spell = get_object_or_404(Spell, spell_id=spell_id)

            # Rozpocznij naukę spella
            creature.learning_spell_id = spell_id
            creature.learning_start_time = serializer.validated_data['learning_start_time']
            creature.learning_end_time = serializer.validated_data['learning_end_time']
            creature.learning_is_complete = False
            creature.save()

            response_serializer = CreatureSerializer(creature)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsSpellCompleteView(APIView):
    """POST: Oznacz spell jako nauczony"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=SpellCompleteSerializer, responses=CreatureSerializer)
    def post(self, request):
        try:
            serializer = SpellCompleteSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            creature_id = serializer.validated_data['creature_id']
            spell_id = serializer.validated_data['spell_id']

            creature = get_object_or_404(Creature, id=creature_id)

            # Sprawdź czy użytkownik jest właścicielem creature
            if creature.owner != request.user.player:
                return Response({'error': 'Nie masz dostępu do tego stworka'},
                              status=status.HTTP_403_FORBIDDEN)

            # Sprawdź czy creature właśnie uczy się tego spella
            if creature.learning_spell_id != spell_id or not creature.learning_is_complete:
                return Response({'error': 'Ten spell nie jest w trakcie nauki'},
                              status=status.HTTP_400_BAD_REQUEST)

            # Oznacz jako nauczony (w tej wersji po prostu usuwamy informacje o nauce)
            creature.learning_spell_id = None
            creature.learning_start_time = None
            creature.learning_end_time = None
            creature.learning_is_complete = False
            creature.save()

            response_serializer = CreatureSerializer(creature)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Views for Cities
class ZawomonsCityListView(APIView):
    """GET: Lista wszystkich miast"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CitySerializer(many=True))
    def get(self, request):
        try:
            cities = City.objects.all()
            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsCityCreateView(APIView):
    """POST: Stwórz nowe miasto"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=CityCreateSerializer, responses=CitySerializer)
    def post(self, request):
        try:
            player = request.user.player

            serializer = CityCreateSerializer(data=request.data)
            if serializer.is_valid():
                city = serializer.save(owner=player)
                response_serializer = CitySerializer(city)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Views for Battles
class ZawomonsBattleListView(APIView):
    """GET: Lista bitew gracza"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=BattleSerializer(many=True))
    def get(self, request):
        try:
            player = request.user.player
            battles = Battle.objects.filter(
                player1=player
            ) | Battle.objects.filter(
                player2=player
            ).order_by('-created_at')

            serializer = BattleSerializer(battles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

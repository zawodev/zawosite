from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Player, Creature, Spell, City
from .serializers import (PlayerSerializer,
                         PlayerListSerializer,
                         CreatureSerializer, SpellSerializer,
                         CitySerializer)
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta

# Create your views here.

# --- 1. player endpoints
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

class ZawomonsPlayerMeView(APIView):
    """GET: Pobierz wszystkie dane gracza w tym: listę creatures, listę cities, ilości zasobów, experience, last_creature_claim_time"""
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

class ZawomonsPlayerMeFriendsView(APIView):
    """GET: Friend list gracza"""
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

class ZawomonsPlayerDetailView(APIView):
    """GET: Pobranie danych innego gracza po kliknięciu w jego profil w grze"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=PlayerListSerializer)
    def get(self, request, player_id):
        try:
            player = get_object_or_404(Player, id=player_id)
            # Zwracamy ograniczone dane (jak w PlayerListSerializer) dla bezpieczeństwa
            serializer = PlayerListSerializer(player)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- b) me player creature endpoints
class ZawomonsPlayerMeCreaturesListView(APIView):
    """GET: Lista stworków gracza"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CreatureSerializer(many=True))
    def get(self, request):
        try:
            player = get_object_or_404(Player, user=request.user)
            creatures = Creature.objects.filter(owner=player)
            serializer = CreatureSerializer(creatures, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayerMeCreatureDetailView(APIView):
    """GET: Pobiera dane danego stworka gracza (jeśli należy do gracza)
    PUT: Aktualizuje naszego stworka, na przykład zmienia jego nazwę (ale nie statystyki)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CreatureSerializer)
    def get(self, request, creature_id):
        try:
            player = get_object_or_404(Player, user=request.user)
            creature = get_object_or_404(Creature, id=creature_id, owner=player)
            serializer = CreatureSerializer(creature)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(request={'type': 'object', 'properties': {'name': {'type': 'string'}}}, responses=CreatureSerializer)
    def put(self, request, creature_id):
        try:
            player = get_object_or_404(Player, user=request.user)
            creature = get_object_or_404(Creature, id=creature_id, owner=player)
            
            # Tylko nazwa może być zmieniana przez gracza
            print(request.data)
            new_name = request.data.get('name')
            if new_name:
                creature.name = new_name[:50]  # Ograniczenie długości
                creature.save()

            serializer = CreatureSerializer(creature)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayerMeCreatureProgressView(APIView):
    """GET: Pobiera tylko progress taska stworka (jeśli stworek należy do gracza)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={'200': {'type': 'object', 'properties': {
        'travel_progress': {'type': 'object'},
        'learning_progress': {'type': 'object'}
    }}})
    def get(self, request, creature_id):
        try:
            player = get_object_or_404(Player, user=request.user)
            creature = get_object_or_404(Creature, id=creature_id, owner=player)
            
            # Przygotuj dane o progressie
            progress_data = {
                'travel_progress': {
                    'is_traveling': bool(creature.travel_start_time and not creature.travel_is_complete),
                    'travel_start_time': creature.travel_start_time,
                    'travel_end_time': creature.travel_end_time,
                    'travel_is_complete': creature.travel_is_complete,
                    'travel_from_x': creature.travel_from_x,
                    'travel_from_y': creature.travel_from_y,
                    'travel_to_x': creature.travel_to_x,
                    'travel_to_y': creature.travel_to_y,
                },
                'learning_progress': {
                    'is_learning': bool(creature.learning_spell_id),
                    'learning_spell_id': creature.learning_spell_id,
                    'learning_start_time': creature.learning_start_time,
                    'learning_end_time': creature.learning_end_time,
                    'learning_is_complete': creature.learning_is_complete,
                }
            }
            
            return Response(progress_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- a) other player endpoints (read-only)
class ZawomonsPlayerCreaturesListView(APIView):
    """GET: Lista stworków innego gracza (do podglądu profilu)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CreatureSerializer(many=True))
    def get(self, request, player_id):
        try:
            player = get_object_or_404(Player, id=player_id)
            creatures = Creature.objects.filter(owner=player)
            serializer = CreatureSerializer(creatures, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Autorytatywne akcje stworków
class ZawomonsPlayerMeCreatureClaimView(APIView):
    """POST: Robi próbę dodania darmowego stworka jeśli minęły 4h od ostatniego last_creature_claim_time"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CreatureSerializer)
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
            if player.last_creature_claim_time and timezone.now() < player.last_creature_claim_time + timedelta(seconds=4):
                time_remaining = (player.last_creature_claim_time + timedelta(hours=4) - timezone.now()).total_seconds()
                return Response({
                    'error': 'Możesz odebrać nowego stworka tylko raz na 4 godziny',
                    'time_remaining_seconds': int(time_remaining)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Backend generuje stworka z losowymi statystykami (autorytatywnie)
            import random
            elements = ['fire', 'water', 'ice', 'none']
            main_element = random.choice(elements)
            
            # Generuj losowy kolor
            color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
            
            # Losowe statystyki bazowe (backend decyduje)
            base_hp = random.randint(1, 4)
            base_energy = random.randint(1, 6)
            base_damage = random.randint(1, 2)
            base_initiative = random.randint(1, 5)
            
            # Stwórz stworka
            creature = Creature.objects.create(
                owner=player,
                name=f"Wild {main_element.capitalize()}",
                main_element=main_element,
                color=color,
                experience=0,
                max_hp=base_hp,
                current_hp=base_hp,
                max_energy=base_energy,
                current_energy=base_energy,
                damage=base_damage,
                initiative=base_initiative,
                posX=0.0,
                posY=0.0
            )

            # Automatycznie przypisz spell "Basic Attack" (ID 0) do nowego stworka
            from .models import CreatureSpell
            try:
                basic_attack_spell = Spell.objects.get(spell_id=0)
                CreatureSpell.objects.create(creature=creature, spell=basic_attack_spell)
            except Spell.DoesNotExist:
                # Jeśli Basic Attack nie istnieje, zaloguj błąd ale nie przerywaj tworzenia stworka
                pass

            # chwilowo dla testu ucz również id 1
            try:
                spell_1 = Spell.objects.get(spell_id=1)
                CreatureSpell.objects.create(creature=creature, spell=spell_1)
            except Spell.DoesNotExist:
                pass

            # Zaktualizuj czas ostatniego odbioru stworka
            player.last_creature_claim_time = timezone.now()
            player.save()

            # Zwróć szczegóły stworzonego stworka
            serializer = CreatureSerializer(creature)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayerMeCreatureSpellLearnView(APIView):
    """POST: Zaczyna naukę spella (jeśli stworek nie uczy się już innego spella, ma zasoby gracz i stworek ma wystarczająco dużo energii)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request={'type': 'object', 'properties': {'spell_id': {'type': 'integer'}}}, responses=CreatureSerializer)
    def post(self, request, creature_id):
        try:
            player = get_object_or_404(Player, user=request.user)
            creature = get_object_or_404(Creature, id=creature_id, owner=player)
            
            spell_id = request.data.get('spell_id')
            if not spell_id:
                return Response({'error': 'Musisz podać spell_id'}, status=status.HTTP_400_BAD_REQUEST)

            # Sprawdź czy spell istnieje
            spell = get_object_or_404(Spell, spell_id=spell_id)
            
            # Sprawdź czy stworek nie uczy się już innego spella
            if creature.learning_spell_id:
                return Response({'error': 'Stworek już uczy się innego spella'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Sprawdź czy stworek ma wystarczająco energii (minimum 20)
            if creature.current_energy < 20:
                return Response({'error': 'Stworek nie ma wystarczająco energii (minimum 20)'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Sprawdź zasoby gracza (koszt: 10 gold, 5 gems)
            if player.gold < 10:
                return Response({'error': 'Nie masz wystarczająco złota (potrzeba 10)'}, status=status.HTTP_400_BAD_REQUEST)
            if player.gems < 5:
                return Response({'error': 'Nie masz wystarczająco gemów (potrzeba 5)'}, status=status.HTTP_400_BAD_REQUEST)

            # Pobierz zasoby
            player.gold -= 10
            player.gems -= 5
            player.save()
            
            # Zmniejsz energię stworka
            creature.current_energy -= 20
            
            # Rozpocznij naukę (2 godziny)
            now = timezone.now()
            creature.learning_spell_id = spell_id
            creature.learning_start_time = now
            creature.learning_end_time = now + timedelta(hours=2)
            creature.learning_is_complete = False
            creature.save()

            serializer = CreatureSerializer(creature)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayerMeCreatureTravelStartView(APIView):
    """POST: Zaczyna podróż (jeśli stworek nie jest już w podróży, ma zasoby gracz i stworek ma wystarczająco dużo energii)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request={'type': 'object', 'properties': {
        'destination_x': {'type': 'number'},
        'destination_y': {'type': 'number'}
    }}, responses=CreatureSerializer)
    def post(self, request, creature_id):
        try:
            player = get_object_or_404(Player, user=request.user)
            creature = get_object_or_404(Creature, id=creature_id, owner=player)
            
            destination_x = request.data.get('destination_x')
            destination_y = request.data.get('destination_y')
            
            if destination_x is None or destination_y is None:
                return Response({'error': 'Musisz podać destination_x i destination_y'}, status=status.HTTP_400_BAD_REQUEST)

            # Sprawdź czy stworek nie jest już w podróży
            if creature.travel_start_time and not creature.travel_is_complete:
                return Response({'error': 'Stworek jest już w podróży'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Sprawdź czy stworek ma wystarczająco energii (minimum 15)
            if creature.current_energy < 15:
                return Response({'error': 'Stworek nie ma wystarczająco energii (minimum 15)'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Sprawdź zasoby gracza (koszt: 5 gold)
            if player.gold < 5:
                return Response({'error': 'Nie masz wystarczająco złota (potrzeba 5)'}, status=status.HTTP_400_BAD_REQUEST)

            # Oblicz czas podróży na podstawie dystansu
            import math
            distance = math.sqrt((destination_x - creature.posX)**2 + (destination_y - creature.posY)**2)
            travel_hours = max(1, int(distance / 10))  # Minimum 1 godzina, 1 godzina na każde 10 jednostek
            
            # Pobierz zasoby
            player.gold -= 5
            player.save()
            
            # Zmniejsz energię stworka
            creature.current_energy -= 15
            
            # Rozpocznij podróż
            now = timezone.now()
            creature.travel_from_x = creature.posX
            creature.travel_from_y = creature.posY
            creature.travel_to_x = float(destination_x)
            creature.travel_to_y = float(destination_y)
            creature.travel_start_time = now
            creature.travel_end_time = now + timedelta(hours=travel_hours)
            creature.travel_is_complete = False
            creature.save()

            serializer = CreatureSerializer(creature)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- 1. player tasks endpoint
class ZawomonsPlayerMeTasksView(APIView):
    """GET: All ongoing tasks for the player (all creatures + all cities) - travel, learning, merging, city upgrade etc."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={'200': {'type': 'object'}})
    def get(self, request):
        try:
            player = get_object_or_404(Player, user=request.user)
            
            # Zbierz zadania z creatures
            creature_tasks = []
            for creature in Creature.objects.filter(owner=player):
                task = {'creature_id': creature.id, 'creature_name': creature.name}
                
                # Sprawdź zadanie podróży
                if creature.travel_start_time and not creature.travel_is_complete:
                    task['travel'] = {
                        'type': 'travel',
                        'start_time': creature.travel_start_time,
                        'end_time': creature.travel_end_time,
                        'from_x': creature.travel_from_x,
                        'from_y': creature.travel_from_y,
                        'to_x': creature.travel_to_x,
                        'to_y': creature.travel_to_y,
                        'is_complete': creature.travel_is_complete
                    }
                
                # Sprawdź zadanie nauki spella
                if creature.learning_spell_id:
                    task['learning'] = {
                        'type': 'spell_learning',
                        'spell_id': creature.learning_spell_id,
                        'start_time': creature.learning_start_time,
                        'end_time': creature.learning_end_time,
                        'is_complete': creature.learning_is_complete
                    }
                
                # Dodaj tylko jeśli ma jakieś zadania
                if 'travel' in task or 'learning' in task:
                    creature_tasks.append(task)
            
            # Zbierz zadania z miast (placeholder - później rozszerzymy)
            city_tasks = []
            # TODO: Dodać zadania miast (upgrade, building, resource generation)
            
            response_data = {
                'creature_tasks': creature_tasks,
                'city_tasks': city_tasks,
                'total_tasks': len(creature_tasks) + len(city_tasks)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- c) me player city endpoints
class ZawomonsPlayerMeCitiesListView(APIView):
    """GET: Lista miast gracza"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CitySerializer(many=True))
    def get(self, request):
        try:
            player = get_object_or_404(Player, user=request.user)
            cities = City.objects.filter(owner=player)
            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayerMeCityDetailView(APIView):
    """GET: Pobiera dane danego miasta gracza"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CitySerializer)
    def get(self, request, city_id):
        try:
            player = get_object_or_404(Player, user=request.user)
            city = get_object_or_404(City, id=city_id, owner=player)
            serializer = CitySerializer(city)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPlayerMeCityBuildView(APIView):
    """POST: Buduje nowe miasto (jeśli gracz ma wystarczająco dużo zasobów)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request={'type': 'object', 'properties': {
        'name': {'type': 'string'},
        'pos_x': {'type': 'number'},
        'pos_y': {'type': 'number'}
    }}, responses=CitySerializer)
    def post(self, request):
        try:
            player = get_object_or_404(Player, user=request.user)
            
            name = request.data.get('name')
            pos_x = request.data.get('pos_x')
            pos_y = request.data.get('pos_y')
            
            if not name or pos_x is None or pos_y is None:
                return Response({'error': 'Musisz podać name, pos_x i pos_y'}, status=status.HTTP_400_BAD_REQUEST)

            # Sprawdź zasoby gracza (koszt budowy miasta: 100 gold, 50 wood, 30 stone)
            if player.gold < 100:
                return Response({'error': 'Nie masz wystarczająco złota (potrzeba 100)'}, status=status.HTTP_400_BAD_REQUEST)
            if player.wood < 50:
                return Response({'error': 'Nie masz wystarczająco drewna (potrzeba 50)'}, status=status.HTTP_400_BAD_REQUEST)
            if player.stone < 30:
                return Response({'error': 'Nie masz wystarczająco kamienia (potrzeba 30)'}, status=status.HTTP_400_BAD_REQUEST)

            # Pobierz zasoby
            player.gold -= 100
            player.wood -= 50
            player.stone -= 30
            player.save()
            
            # Stwórz miasto
            city = City.objects.create(
                owner=player,
                name=name[:100],  # Ograniczenie długości
                posX=float(pos_x),
                posY=float(pos_y),
                description=f"City founded by {player.user.username}"
            )

            serializer = CitySerializer(city)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- 2. public endpoints (read-only for all)
class ZawomonsPublicCreaturesListView(APIView):
    """GET: Lista wszystkich stworków (dzikich i należących do graczy)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CreatureSerializer(many=True))
    def get(self, request):
        try:
            creatures = Creature.objects.all()
            serializer = CreatureSerializer(creatures, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPublicCreatureDetailView(APIView):
    """GET: Pobiera dane danego stworka (dowolnego nie tylko danego gracza)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CreatureSerializer)
    def get(self, request, creature_id):
        try:
            creature = get_object_or_404(Creature, id=creature_id)
            serializer = CreatureSerializer(creature)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPublicCitiesListView(APIView):
    """GET: Lista miast (wszystkich)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CitySerializer(many=True))
    def get(self, request):
        try:
            cities = City.objects.all()
            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPublicCityDetailView(APIView):
    """GET: Pobiera dane danego miasta (dowolnego nie tylko danego gracza)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CitySerializer)
    def get(self, request, city_id):
        try:
            city = get_object_or_404(City, id=city_id)
            serializer = CitySerializer(city)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ZawomonsPublicSpellsListView(APIView):
    """GET: Lista wszystkich spelli w grze (statyczna)"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=SpellSerializer(many=True))
    def get(self, request):
        try:
            spells = Spell.objects.all()
            serializer = SpellSerializer(spells, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

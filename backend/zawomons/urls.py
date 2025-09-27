from django.urls import path
from .views import (ZawomonsPlayersListView,
                   ZawomonsPlayerMeView, ZawomonsPlayerMeFriendsView,
                   ZawomonsPlayerDetailView, ZawomonsPlayerMeCreaturesListView,
                   ZawomonsPlayerMeCreatureDetailView, ZawomonsPlayerMeCreatureProgressView,
                   ZawomonsPlayerCreaturesListView, ZawomonsPlayerMeCreatureClaimView,
                   ZawomonsPlayerMeCreatureSpellLearnView,
                   ZawomonsPlayerMeCreatureTravelStartView, ZawomonsPlayerMeTasksView,
                   ZawomonsPlayerMeCitiesListView, ZawomonsPlayerMeCityDetailView,
                   ZawomonsPlayerMeCityBuildView, ZawomonsPublicCreaturesListView,
                   ZawomonsPublicCreatureDetailView, ZawomonsPublicCitiesListView,
                   ZawomonsPublicCityDetailView, ZawomonsPublicSpellsListView)

urlpatterns = [
    # --- 1. player endpoints
    # ✅ GET  /zawomons/players/ - global player list
    path('players/', ZawomonsPlayersListView.as_view(), name='zawomons-players-list'),
    
    # ✅ GET  /zawomons/players/me/ - pobiera wszystkie dane gracza
    path('players/me/', ZawomonsPlayerMeView.as_view(), name='zawomons-players-me'),
    
    # ✅ GET  /zawomons/players/me/friends/ - friend list
    path('players/me/friends/', ZawomonsPlayerMeFriendsView.as_view(), name='zawomons-players-me-friends'),
    
    # ✅ GET  /zawomons/players/<id>/ - pobranie danych innego gracza
    path('players/<int:player_id>/', ZawomonsPlayerDetailView.as_view(), name='zawomons-players-detail'),
    
    # ✅ GET  /zawomons/players/<id>/creatures/ - lista stworków innego gracza (do podglądu profilu)
    path('players/<int:player_id>/creatures/', ZawomonsPlayerCreaturesListView.as_view(), name='zawomons-players-creatures'),
    
    # - b) me player creature endpoints
    # ✅ GET  /zawomons/players/me/creatures/ - lista stworków gracza
    path('players/me/creatures/', ZawomonsPlayerMeCreaturesListView.as_view(), name='zawomons-players-me-creatures'),
    
    # ✅ GET/PUT  /zawomons/players/me/creatures/<id>/ - pobiera dane danego stworka gracza / aktualizuje stworka
    path('players/me/creatures/<int:creature_id>/', ZawomonsPlayerMeCreatureDetailView.as_view(), name='zawomons-players-me-creatures-detail'),
    
    # ✅ GET  /zawomons/players/me/creatures/<id>/progress/ - pobiera tylko progress taska (jeśli stworek należy do gracza)
    path('players/me/creatures/<int:creature_id>/progress/', ZawomonsPlayerMeCreatureProgressView.as_view(), name='zawomons-players-me-creatures-progress'),
    
    # ✅ POST /zawomons/players/me/creatures/claim/ - robi próbę dodania darmowego stworka jeśli minęły 4h od ostatniego last_creature_claim_time
    path('players/me/creatures/claim/', ZawomonsPlayerMeCreatureClaimView.as_view(), name='zawomons-players-me-creatures-claim'),
    
    # ✅ POST /zawomons/players/me/creatures/<id>/spells/learn/ - zaczyna naukę spella
    path('players/me/creatures/<int:creature_id>/spells/learn/', ZawomonsPlayerMeCreatureSpellLearnView.as_view(), name='zawomons-players-me-creatures-spells-learn'),
    
    # ✅ POST /zawomons/players/me/creatures/<id>/travel/start/ - zaczyna podróż
    path('players/me/creatures/<int:creature_id>/travel/start/', ZawomonsPlayerMeCreatureTravelStartView.as_view(), name='zawomons-players-me-creatures-travel-start'),
    
    # ✅ GET  /zawomons/players/me/tasks/ - all ongoing tasks for the player (all creatures + all cities)
    path('players/me/tasks/', ZawomonsPlayerMeTasksView.as_view(), name='zawomons-players-me-tasks'),
    
    # - c) me player city endpoints
    # ✅ GET  /zawomons/players/me/cities/ - lista miast gracza
    path('players/me/cities/', ZawomonsPlayerMeCitiesListView.as_view(), name='zawomons-players-me-cities'),
    
    # ✅ GET  /zawomons/players/me/cities/<id>/ - pobiera dane danego miasta gracza
    path('players/me/cities/<int:city_id>/', ZawomonsPlayerMeCityDetailView.as_view(), name='zawomons-players-me-cities-detail'),
    
    # ✅ POST /zawomons/players/me/cities/build/ - buduje nowe miasto (jeśli gracz ma wystarczająco dużo zasobów)
    path('players/me/cities/build/', ZawomonsPlayerMeCityBuildView.as_view(), name='zawomons-players-me-cities-build'),
    
    # --- 2. public endpoints (read-only for all)
    # ✅ GET  /zawomons/creatures/ - lista wszystkich stworków (dzikich i należących do graczy)
    path('creatures/', ZawomonsPublicCreaturesListView.as_view(), name='zawomons-creatures-list'),
    
    # ✅ GET  /zawomons/creatures/<id>/ - pobiera dane danego stworka (dowolnego nie tylko danego gracza)
    path('creatures/<int:creature_id>/', ZawomonsPublicCreatureDetailView.as_view(), name='zawomons-creatures-detail'),
    
    # ✅ GET  /zawomons/cities/ - lista miast (wszystkich)
    path('cities/', ZawomonsPublicCitiesListView.as_view(), name='zawomons-cities-list'),
    
    # ✅ GET  /zawomons/cities/<id>/ - pobiera dane danego miasta (dowolnego nie tylko danego gracza)
    path('cities/<int:city_id>/', ZawomonsPublicCityDetailView.as_view(), name='zawomons-cities-detail'),
    
    # ✅ GET  /zawomons/spells/ - lista wszystkich spelli w grze (statyczna)
    path('spells/', ZawomonsPublicSpellsListView.as_view(), name='zawomons-spells-list'),
]


# --- 1. player endpoints
# ✅ GET  /zawomons/players/ - global player list (ale nie wszystkie ich dane tylko niektóre dla krótszego payloadu (do listy znajomych potrzebne)
# ✅ GET  /zawomons/players/me/ - pobiera wszystkie dane gracza w tym: listę creatures, listę cities, ilości zasobów, experience, last_creature_claim_time (raz na starcie gry dla synchronizacji klienta z backendem)
# ✅ GET  /zawomons/players/me/friends/ - friend list (podobnie jak global player list nie wszystkie dane tylko friend list)
# ✅ GET  /zawomons/players/me/tasks/ - all ongoing tasks for the player (all creatures + all cities) (e.g., travel, learning, merging, city upgrade etc.)

# - a) other player endpoints (read-only)
# ✅ GET  /zawomons/players/<id>/ - pobranie danych innego gracza po kliknięciu w jego profil w grze
# ✅ GET  /zawomons/players/<id>/creatures/ - lista stworków innego gracza (do podglądu profilu)
# ❌ GET  /zawomons/players/<id>/cities/ - lista miast innego gracza (do podglądu profilu)
# ❌ GET  /zawomons/players/<id>/battles/ - lista bitew innego gracza (do podglądu profilu)

# - b) me player creature endpoints
# ✅ GET  /zawomons/players/me/creatures/ - lista stworków gracza
# ✅ GET  /zawomons/players/me/creatures/<id>/ - pobiera dane danego stworka gracza (jeśli należy do gracza)
# ✅ GET  /zawomons/players/me/creatures/<id>/progress/ - pobiera tylko progress taska (jeśli stworek należy do gracza) - np. ile zostało do końca nauki spella, podróży itp.

# ✅ PUT  /zawomons/players/me/creatures/<id>/ - aktualizuje naszego stworka, na przykład zmienia jego nazwę (ale nie statystyki)

# ✅ POST /zawomons/players/me/creatures/claim/ - robi próbę dodania darmowego stworka jeśli minęły 4h od ostatniego last_creature_claim_time w player data
# ❌ POST /zawomons/players/me/creatures/merge/ - łączy dwa stworki w jeden (jeśli oba należą do gracza i mają ten sam main_element i wystarczająco dużo doświadczenia)
# ✅ POST /zawomons/players/me/creatures/<id>/spells/learn/ - zaczyna naukę spella (jeśli stworek nie uczy się już innego spella, ma zasoby gracz i stworek ma wystarczająco dużo energii)
# ✅ POST /zawomons/players/me/creatures/<id>/travel/start/ - zaczyna podróż (jeśli stworek nie jest już w podróży, ma zasoby gracz i stworek ma wystarczająco dużo energii)

# - c) me player city endpoints
# ✅ GET  /zawomons/players/me/cities/ - lista miast gracza
# ✅ GET  /zawomons/players/me/cities/<id>/ - pobiera dane danego miasta gracza
# ❌ GET  /zawomons/players/me/cities/<id>/progress/ - pobiera tylko progress taska (jeśli miasto należy do gracza) - np. ile zostało do końca budowy, ulepszenia itp.

# ❌ PUT  /zawomons/players/me/cities/<id>/ - aktualizuje miasto, na przykład zmienia jego nazwę (ale nie statystyki)

# ✅ POST /zawomons/players/me/cities/build - buduje nowe miasto (jeśli gracz ma wystarczająco dużo zasobów)
# ❌ POST /zawomons/players/me/cities/<id>/upgrade/ - ulepsza miasto (jeśli należy do gracza i ma wystarczająco dużo zasobów)
# ❌ POST /zawomons/players/me/cities/<id>/resources/collect/ - claim resources generated by a city

# - d) me player battle endpoints
# ❌ GET  /zawomons/players/me/battles/ - lista bitew gracza (zarówno zakończonych jak i trwających)

# --- 2. public endpoints (read-only for all, unless stated otherwise)
# ✅ GET  /zawomons/creatures/ - lista wszystkich stworków (dzikich i należących do graczy)
# ✅ GET  /zawomons/creatures/<id>/ - pobiera dane danego stworka (dowolnego nie tylko danego gracza)

# ✅ GET  /zawomons/cities/ - lista miast (wszystkich)
# ✅ GET  /zawomons/cities/<id>/ - pobiera dane danego miasta (dowolnego nie tylko danego gracza)

# ✅ GET  /zawomons/spells/ - lista wszystkich spelli w grze (statyczna)

# ❌ GET  /zawomons/battles/ - lista wszystkich bitew (publicznych i prywatnych)
# ❌ GET  /zawomons/battles/<id>/ - pobiera dane danej bitwy



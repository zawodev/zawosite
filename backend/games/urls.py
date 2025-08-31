from django.urls import path
from .views import (GameList, ZawomonsPlayerDataGetView, 
                   ZawomonsSetSingleResourceView, ZawomonsPlayersListView,
                   ZawomonsFriendsListView, ZawomonsCreatureGetView, 
                   ZawomonsCreatureAddView, ZawomonsCreatureSetView, 
                   ZawomonsSpellLearnView, ZawomonsSpellCompleteView)

urlpatterns = [
    # Ogólne endpointy gier
    path('', GameList.as_view(), name='game-list'),
    
    # Endpointy specyficzne dla gry Zawomons
    path('zawomons/player-data-get/', ZawomonsPlayerDataGetView.as_view(), name='zawomons-player-data-get'),
    path('zawomons/set-single-resource/', ZawomonsSetSingleResourceView.as_view(), name='zawomons-set-single-resource'),
    path('zawomons/players/', ZawomonsPlayersListView.as_view(), name='zawomons-players-list'),
    path('zawomons/friends/', ZawomonsFriendsListView.as_view(), name='zawomons-friends-list'),
    
    # Endpointy dla zarządzania stworkami
    path('zawomons/creature-get/<int:creature_id>/', ZawomonsCreatureGetView.as_view(), name='zawomons-creature-get'),
    path('zawomons/creature-add/', ZawomonsCreatureAddView.as_view(), name='zawomons-creature-add'),
    path('zawomons/creature-set/', ZawomonsCreatureSetView.as_view(), name='zawomons-creature-set'),
    
    # Endpointy dla zarządzania spellami
    path('zawomons/spell-learn/', ZawomonsSpellLearnView.as_view(), name='zawomons-spell-learn'),
    path('zawomons/spell-complete/', ZawomonsSpellCompleteView.as_view(), name='zawomons-spell-complete'),
] 
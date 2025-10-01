from django.urls import path
from .battle_views import (
    CreateBattleView,
    JoinBattleView, 
    BattleListView,
    BattleDetailView,
    OpenBattlesView
)

battle_urlpatterns = [
    path('battles/create/', CreateBattleView.as_view(), name='create-battle'),
    path('battles/join/', JoinBattleView.as_view(), name='join-battle'),
    path('battles/', BattleListView.as_view(), name='battle-list'),
    path('battles/<uuid:battle_id>/', BattleDetailView.as_view(), name='battle-detail'),
    path('battles/open/', OpenBattlesView.as_view(), name='open-battles'),
]
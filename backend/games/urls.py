from django.urls import path
from .views import GameList

urlpatterns = [
    # Ogólne endpointy gier
    path('', GameList.as_view(), name='game-list'),
] 
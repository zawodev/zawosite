from django.urls import path
from .views import GameList, GameDetail, GameSaveListCreate, GameSaveDetail, GameSaveForUser, GameSaveForFriends

urlpatterns = [
    path('', GameList.as_view(), name='game-list'),
    path('<int:pk>/', GameDetail.as_view(), name='game-detail'),
    path('saves/', GameSaveListCreate.as_view(), name='game-save-list-create'),
    path('saves/<int:pk>/', GameSaveDetail.as_view(), name='game-save-detail'),
    path('saves/user/<int:user_id>/', GameSaveForUser.as_view(), name='game-save-for-user'),
    path('saves/friends/', GameSaveForFriends.as_view(), name='game-save-for-friends'),
] 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameCommentViewSet, DirectCommentViewSet

# Router for game-specific comment operations
game_router = DefaultRouter()
game_router.register(r'comments/(?P<game_slug>[^/.]+)', GameCommentViewSet, basename='game-comment')

# Router for direct comment operations (by ID only)
direct_router = DefaultRouter()
direct_router.register(r'comment', DirectCommentViewSet, basename='comment-direct')

urlpatterns = [
    path('', include(game_router.urls)),
    path('', include(direct_router.urls)),
]

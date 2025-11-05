from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameCommentViewSet

router = DefaultRouter()
router.register(r'comments/(?P<game_slug>[^/.]+)', GameCommentViewSet, basename='game-comment')

urlpatterns = [
    path('', include(router.urls)),
]

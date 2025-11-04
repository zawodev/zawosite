from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LobbyViewSet

router = DefaultRouter()
router.register(r'lobbies', LobbyViewSet, basename='lobby')

urlpatterns = [
    path('', include(router.urls)),
]

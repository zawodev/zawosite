from django.urls import path
from .views import UserProfileView, UserListView, FriendsListView, AddFriendView, RemoveFriendView, UserDetailView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

urlpatterns = [
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('', UserListView.as_view(), name='user-list'),
    path('friends/', FriendsListView.as_view(), name='friends-list'),
    path('friends/add/', AddFriendView.as_view(), name='add-friend'),
    path('friends/remove/', RemoveFriendView.as_view(), name='remove-friend'),
    path('<str:username>/', UserDetailView.as_view(), name='user-detail'),
]

router = DefaultRouter()
router.register(r'viewset', UserViewSet, basename='user-viewset')

urlpatterns += router.urls 
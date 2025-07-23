from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, FriendSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from dj_rest_auth.utils import jwt_encode
from django.conf import settings
import urllib.parse
import json
from rest_framework_simplejwt.tokens import RefreshToken
import logging
logger = logging.getLogger(__name__)
from django.views import View
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login as auth_login
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView
from django.conf import settings
import urllib.parse
import json

# Create your views here.

print(">>> USERS.VIEWS.PY LOADED <<<")

@extend_schema(responses=UserSerializer)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@extend_schema(responses=UserSerializer)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

@extend_schema(responses=FriendSerializer)
class FriendsListView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()

@extend_schema(request=None, responses=None)
class AddFriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        friend_id = request.data.get('friend_id')
        try:
            friend = User.objects.get(id=friend_id)
            request.user.friends.add(friend)
            return Response({'status': 'friend added'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(request=None, responses=None)
class RemoveFriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        friend_id = request.data.get('friend_id')
        try:
            friend = User.objects.get(id=friend_id)
            request.user.friends.remove(friend)
            return Response({'status': 'friend removed'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema_view(
    list=extend_schema(responses=UserSerializer),
    retrieve=extend_schema(responses=UserSerializer),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        params = {
            "token": token,
            "user": json.dumps(user_data)
        }
        url = settings.FRONTEND_URL + "/auth/callback?" + urllib.parse.urlencode(params)
        print(f"[SSO REDIRECT] user={user.username} token={token} url={url}")
        return url

class SocialLoginCallbackView(View):
    def get(self, request, *args, **kwargs):
        # Użytkownik powinien być już zalogowany przez allauth
        user = request.user
        if not user.is_authenticated:
            # Jeśli nie, przekieruj na frontend bez tokena
            return HttpResponseRedirect(settings.FRONTEND_URL + "/auth/callback?error=not_authenticated")
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        params = {
            "token": token,
            "user": json.dumps(user_data)
        }
        url = settings.FRONTEND_URL + "/auth/callback?" + urllib.parse.urlencode(params)
        print(f"[CUSTOM SSO CALLBACK] user={user.username} token={token} url={url}")
        return HttpResponseRedirect(url)

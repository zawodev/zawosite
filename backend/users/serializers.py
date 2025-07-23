from rest_framework import serializers
from .models import User
from dj_rest_auth.registration.serializers import RegisterSerializer

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'description', 'friends', 'role'] 

class CustomRegisterSerializer(RegisterSerializer):
    _has_phone_field = False
    def validate(self, data):
        # Usuwamy pole phone, jeśli przypadkiem się pojawi
        data.pop('phone', None)
        return super().validate(data) 
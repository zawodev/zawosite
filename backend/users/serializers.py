from rest_framework import serializers
from .models import User
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'avatar_url', 'provider', 'avatar', 'description', 'friends', 'role']
    
    def get_full_name(self, obj):
        """Return full name or username if not set"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        return obj.username
    
    def get_avatar_url(self, obj):
        """Return avatar URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def get_provider(self, obj):
        """Get OAuth provider if any"""
        try:
            from allauth.socialaccount.models import SocialAccount
            social_account = SocialAccount.objects.filter(user=obj).first()
            if social_account:
                return social_account.provider
        except:
            pass
        return 'local' 

class CustomRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    def validate_username(self, username):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return username
    
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data
    
    def save(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.create_user(
            username=self.validated_data['username'],
            email=f"{self.validated_data['username']}@placeholder.com",
            password=self.validated_data['password1']
        )
        return user

class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg, code='authorization')
                
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(_('Must include "username" and "password".'), code='authorization') 
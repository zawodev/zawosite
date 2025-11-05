from rest_framework import serializers
from .models import GameComment, CommentVote


class CommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentVote
        fields = ['id', 'vote_type', 'created_at']


class GameCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    upvotes_count = serializers.IntegerField(read_only=True)
    downvotes_count = serializers.IntegerField(read_only=True)
    karma = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = GameComment
        fields = [
            'id', 'game_slug', 'parent', 'username', 'avatar_url', 'content',
            'created_at', 'updated_at', 'is_edited', 'upvotes_count', 'downvotes_count',
            'karma', 'user_vote', 'replies_count', 'can_edit', 'can_delete'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_edited']
    
    def get_avatar_url(self, obj):
        if hasattr(obj.user, 'avatar') and obj.user.avatar:
            return obj.user.avatar.url
        return None
    
    def get_user_vote(self, obj):
        """Get current user's vote on this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            if vote:
                return vote.vote_type
        return None
    
    def get_can_edit(self, obj):
        """Check if current user can edit this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user or request.user.is_staff
        return False


class CreateCommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=GameComment.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = GameComment
        fields = ['content', 'parent']
    
    def validate_content(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long")
        return value.strip()
    
    def validate_parent(self, value):
        """Ensure parent exists and is not itself a reply (max 1 level deep)"""
        if value and value.parent is not None:
            raise serializers.ValidationError("Cannot reply to a reply. Only one level of nesting allowed.")
        return value


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameComment
        fields = ['content']
    
    def validate_content(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long")
        return value.strip()
    
    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.is_edited = True
        instance.save()
        return instance

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
    
    class Meta:
        model = GameComment
        fields = [
            'id', 'game_slug', 'username', 'avatar_url', 'content',
            'created_at', 'updated_at', 'upvotes_count', 'downvotes_count',
            'karma', 'user_vote'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
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


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameComment
        fields = ['content']
    
    def validate_content(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long")
        return value.strip()

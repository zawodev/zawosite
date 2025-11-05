from django.contrib import admin
from .models import GameComment, CommentVote


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_slug', 'user', 'content_preview', 'parent', 'is_edited', 'replies_count', 'karma', 'created_at']
    list_filter = ['game_slug', 'is_edited', 'created_at']
    search_fields = ['content', 'user__username', 'game_slug']
    readonly_fields = ['created_at', 'updated_at', 'upvotes_count', 'downvotes_count', 'karma', 'replies_count']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__username', 'comment__content']
    readonly_fields = ['created_at']

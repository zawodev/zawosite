from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class GameComment(models.Model):
    """Comment for a game"""
    game_slug = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_comments')
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['game_slug', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} on {self.game_slug}: {self.content[:50]}"
    
    @property
    def upvotes_count(self):
        return self.votes.filter(vote_type='up').count()
    
    @property
    def downvotes_count(self):
        return self.votes.filter(vote_type='down').count()
    
    @property
    def karma(self):
        return self.upvotes_count - self.downvotes_count


class CommentVote(models.Model):
    """Vote on a comment (upvote or downvote)"""
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    comment = models.ForeignKey(GameComment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['comment', 'user']]
        indexes = [
            models.Index(fields=['comment', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type}voted {self.comment.id}"

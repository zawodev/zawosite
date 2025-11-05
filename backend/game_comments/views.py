from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Count, Q, F
from .models import GameComment, CommentVote
from .serializers import GameCommentSerializer, CreateCommentSerializer


class GameCommentViewSet(viewsets.ModelViewSet):
    queryset = GameComment.objects.all()
    serializer_class = GameCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = GameComment.objects.all()
        
        # Filter by game slug from URL
        game_slug = self.kwargs.get('game_slug')
        if game_slug:
            queryset = queryset.filter(game_slug=game_slug)
        
        # Sort by karma or date
        sort_by = self.request.query_params.get('sort_by', 'date')  # 'date' or 'karma'
        
        if sort_by == 'karma':
            # Annotate with karma and sort
            queryset = queryset.annotate(
                upvotes=Count('votes', filter=Q(votes__vote_type='up')),
                downvotes=Count('votes', filter=Q(votes__vote_type='down')),
                karma_score=F('upvotes') - F('downvotes')
            ).order_by('-karma_score', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCommentSerializer
        return GameCommentSerializer
    
    def perform_create(self, serializer):
        # Get game_slug from URL and save with the comment
        game_slug = self.kwargs.get('game_slug')
        serializer.save(user=self.request.user, game_slug=game_slug)
    
    def create(self, request, *args, **kwargs):
        """Override create to return full serialized comment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the created comment and serialize it with full serializer
        comment = serializer.instance
        output_serializer = GameCommentSerializer(comment, context={'request': request})
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None, game_slug=None):
        """Upvote or downvote a comment"""
        comment = self.get_object()
        vote_type = request.data.get('vote_type')
        
        if vote_type not in ['up', 'down']:
            return Response(
                {'error': 'vote_type must be "up" or "down"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create vote
        vote, created = CommentVote.objects.get_or_create(
            comment=comment,
            user=request.user,
            defaults={'vote_type': vote_type}
        )
        
        if not created:
            # If vote already exists
            if vote.vote_type == vote_type:
                # Same vote - remove it (toggle off)
                vote.delete()
            else:
                # Different vote - change it
                vote.vote_type = vote_type
                vote.save()
        
        # Return updated comment with vote counts
        serializer = GameCommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_comment(self, request, pk=None):
        """Delete own comment"""
        comment = self.get_object()
        
        # Only allow user to delete their own comments (or admins)
        if comment.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only delete your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

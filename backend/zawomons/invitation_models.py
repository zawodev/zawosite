from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class GameInvitation(models.Model):
    """Model zaproszenia do gry"""
    
    INVITATION_TYPES = [
        ('friendly', 'Friendly Battle'),
        ('ranked', 'Ranked Battle'),
    ]
    
    INVITATION_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # gracze
    sender = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='received_invitations')
    
    # typ zaproszenia
    invitation_type = models.CharField(max_length=10, choices=INVITATION_TYPES, default='friendly')
    status = models.CharField(max_length=10, choices=INVITATION_STATUS, default='pending')
    
    # creatures wybrane przez sender
    sender_creatures = models.JSONField(default=list, help_text="Lista ID creatures wybranych przez wysyłającego")
    
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # zaproszenia wygasają po 2 minutach
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # powiązana walka (gdy zaproszenie zostanie zaakceptowane)
    battle = models.ForeignKey('Battle', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Zaproszenia wygasają po 2 minutach
            self.expires_at = timezone.now() + timezone.timedelta(minutes=2)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def can_respond(self):
        return self.status == 'pending' and not self.is_expired()
    
    def __str__(self):
        return f"Invitation {self.id}: {self.sender.user.username} -> {self.receiver.user.username} ({self.status})"
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        # Możesz dodać inne role według potrzeb
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username

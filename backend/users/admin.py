from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Dodatkowe informacje', {'fields': ('avatar', 'description', 'friends', 'role')}),
    )
    filter_horizontal = ('friends',)

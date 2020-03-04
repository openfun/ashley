"""Admin of the Ashley application."""
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin class for Ashley's User model."""

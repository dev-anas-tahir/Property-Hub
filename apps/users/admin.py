"""
This module contains admin configurations for user-related models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from apps.properties.models import Favorite

User = get_user_model()


class FavoriteInlineForUser(admin.TabularInline):
    """
    Inline admin to show all properties favorited by this user.
    """

    model = Favorite
    extra = 0
    readonly_fields = ("property", "favorited_at")
    verbose_name = "Favorited property"
    verbose_name_plural = "Properties favorited by this user"


class UserAdmin(BaseUserAdmin):
    """
    Extended User admin with favorites inline.
    """

    inlines = [FavoriteInlineForUser]


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

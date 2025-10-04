"""
This module contains URL patterns for user-related operations.
"""

from django.urls import path
from apps.users.views import (
    signup_view,
    login_view,
    profile_view,
    logout_view,
    password_change_view,
)

app_name = "users"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path("change_password/", password_change_view, name="change_password"),
]

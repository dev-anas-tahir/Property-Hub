"""
This module contains URL patterns for user-related operations.
"""

from django.urls import path

from apps.users.views import (
    login_view,
    logout_view,
    password_change_view,
    profile_edit_view,
    profile_view,
    signup_view,
    validate_email_view,
)

app_name = "users"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
    path("logout/", logout_view, name="logout"),
    path("password_change/", password_change_view, name="password_change"),
    # Validation endpoints
    path("validate/email/", validate_email_view, name="validate_email"),
]

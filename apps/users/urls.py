"""
This module contains URL patterns for user-related operations.
"""

from django.urls import path
from apps.users.views import (
    signup_view,
    login_view,
    profile_view,
    profile_edit_view,
    logout_view,
    password_change_view,
    validate_username_view,
    validate_email_view,
)

app_name = "users"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
    path("logout/", logout_view, name="logout"),
    path("change_password/", password_change_view, name="change_password"),
    # Validation endpoints
    path("validate/username/", validate_username_view, name="validate_username"),
    path("validate/email/", validate_email_view, name="validate_email"),
]

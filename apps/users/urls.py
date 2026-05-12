"""
This module contains URL patterns for user-related operations.
"""

from django.urls import path

from apps.users.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    ProfileEditView,
    ProfileView,
    SignupView,
    ValidateEmailView,
)

app_name = "users"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", PasswordChangeView.as_view(), name="password_change"),
    # Validation endpoints
    path("validate/email/", ValidateEmailView.as_view(), name="validate_email"),
]

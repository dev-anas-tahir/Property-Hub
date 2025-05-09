"""
This module contains form classes for user-related operations such as
signing up, logging in, and profile management within the Property Hub application.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from typing import override


class SignUpForm(UserCreationForm):
    """Form for user sign-up."""

    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Inform a valid email address.",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        )

    @override
    def clean(self):
        """Override clean to validate email and username."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            self.add_error("email", "Email is already in use.")

        return cleaned_data


class UpdateProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )

    @override
    def clean(self):
        """Override clean to validate email and username."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        username = cleaned_data.get("username")

        # Get the current user instance
        current_user = self.instance

        # Check if email has changed and is already in use
        if email != current_user.email and User.objects.filter(email=email).exists():
            self.add_error("email", "Email is already in use.")

        # Check if username has changed and is already in use
        if username != current_user.username and User.objects.filter(username=username).exists():
            self.add_error("username", "Username is already in use.")

        return cleaned_data

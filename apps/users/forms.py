"""
This module contains forms for user-related operations.
"""

import string
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


def validate_password_strength(password: str):
    """Raise ValidationError if password doesn't meet strength requirements."""

    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(char in string.punctuation for char in password):
        raise ValidationError("Password must contain at least one special character.")


class SignUpForm(UserCreationForm):
    """Form for user sign-up."""

    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Enter a valid email address.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already in use.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        validate_password_strength(password1)
        return password1


class UpdateProfileForm(forms.ModelForm):
    """Form for updating user profile information (excluding password)."""

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = self.instance

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email != self.current_user.email
            and User.objects.filter(email=email).exists()
        ):
            raise ValidationError("Email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if (
            username != self.current_user.username
            and User.objects.filter(username=username).exists()
        ):
            raise ValidationError("Username is already in use.")
        return username


class CustomPasswordChangeForm(PasswordChangeForm):
    """Form for changing user password."""

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        validate_password_strength(password)
        return password

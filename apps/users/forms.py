"""
This module contains validation utilities and forms for user-related operations.
"""

import string
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_password_strength(password: str):
    """
    Validate password strength requirements.
    
    Args:
        password: The password string to validate
        
    Raises:
        ValidationError: If password doesn't meet strength requirements
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(char in string.punctuation for char in password):
        raise ValidationError("Password must contain at least one special character.")


class LoginForm(forms.Form):
    """
    Form for user login with username and password.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        }),
        error_messages={
            'required': 'Username is required.',
        }
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
        error_messages={
            'required': 'Password is required.',
        }
    )
    
    def clean_username(self):
        """Clean and validate username field."""
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
        return username


class SignupForm(forms.Form):
    """
    Form for user registration with validation.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        }),
        error_messages={
            'required': 'Username is required.',
        }
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
        }
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name',
        }),
        error_messages={
            'required': 'First name is required.',
        }
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name',
        }),
        error_messages={
            'required': 'Last name is required.',
        }
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        }),
        error_messages={
            'required': 'Password is required.',
        }
    )
    
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        }),
        error_messages={
            'required': 'Password confirmation is required.',
        },
        label='Confirm Password'
    )
    
    def clean_username(self):
        """Validate username availability."""
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                raise ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise ValidationError('This email address is already registered.')
        return email
    
    def clean_password(self):
        """Validate password strength."""
        password = self.cleaned_data.get('password')
        if password:
            # Use existing validate_password_strength function
            validate_password_strength(password)
        return password
    
    def clean(self):
        """Validate password confirmation matching."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError({
                    'password_confirm': 'Passwords do not match.'
                })
        
        return cleaned_data


class ProfileForm(forms.Form):
    """
    Form for editing user profile information.
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name',
        }),
        error_messages={
            'required': 'First name is required.',
        }
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name',
        }),
        error_messages={
            'required': 'Last name is required.',
        }
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
        }
    )
    
    def __init__(self, *args, user=None, **kwargs):
        """
        Initialize form with current user instance for email validation.
        
        Args:
            user: The User instance being edited
        """
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        """Validate email uniqueness (excluding current user)."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            # Check if email already exists for a different user
            existing_user = User.objects.filter(email=email).exclude(pk=self.user.pk if self.user else None).first()
            if existing_user:
                raise ValidationError('This email address is already registered.')
        return email

"""
This module contains validation utilities for user-related operations.
"""

import string
from django.core.exceptions import ValidationError


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

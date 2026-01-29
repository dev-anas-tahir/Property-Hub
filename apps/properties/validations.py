"""Validators for property-related fields."""

import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# Phone number validator - Format: +92-3001234567
phone_validator = RegexValidator(
    regex=r'^\+\d{2}-\d{10}$',
    message='Phone number must be in the format +92-3001234567 (country code + 10 digits)',
    code='invalid_phone'
)


# CNIC validator - Format: 12345-1234567-1
cnic_validator = RegexValidator(
    regex=r'^\d{5}-\d{7}-\d$',
    message='CNIC must be in the format 12345-1234567-1',
    code='invalid_cnic'
)


def validate_phone(value):
    """Validate phone number format."""
    phone_validator(value)


def validate_cnic(value):
    """Validate CNIC format."""
    cnic_validator(value)


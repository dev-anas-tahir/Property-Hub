import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_cnic(value):
    if not re.match(r"^\d{5}-\d{7}-\d{1}$", value):
        raise ValidationError("CNIC must be in the format 00000-0000000-0")


def validate_phone(value):
    if not re.match(r"^\+\d{2}-\d{10}$", value):
        raise ValidationError("Phone number must be in the format +00-0000000000")


# Validators
phone_validator = RegexValidator(
    r"^\+?\d{7,15}$",
    message="Enter a valid phone number (7-15 digits, optional leading +).",
)

cnic_validator = RegexValidator(
    r"^\d{5}-\d{7}-\d$",
    message="Enter CNIC in 12345-1234567-1 format.",
)

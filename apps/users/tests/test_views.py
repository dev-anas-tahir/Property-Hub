"""
This module contains test cases for user-related views within the Property Hub application.
It uses pytest and django pytest plugins for testing.
"""

import pytest
from django.contrib.auth.models import User
from apps.properties.models import Property

@pytest.mark.django_db
def test_property_str():
    """Test the string representation of the Property model."""
    user = User.objects.create_user(username="john", password="pass1234")
    property = Property.objects.create(name="Test House", user=user, price=100000, is_published=True, description="Test description", address="Test address")
    assert str(property) == "Test House"

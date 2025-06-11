"""
This module contains test cases for property-related models within the Property Hub application.
It uses pytest and django pytest plugins for testing.
"""

import pytest
from django.urls import reverse
from apps.properties.models import Property


@pytest.mark.django_db
def test_property_str(user):
    """Test the string representation of the Property model."""

    # use the `user` fixture for ownership
    prop = Property.objects.create(
        user=user,
        name="Test House",
        description="Test description",
        full_address="Test address",
        phone_number="+92-3001234567",
        cnic="12345-1234567-1",
        property_type=Property.PropertyType.HOUSE,
        price=100000,
        is_published=True,
    )
    assert str(prop) == "Test House"


@pytest.mark.django_db
def test_property_add_form(user, client):
    """Test adding a new property using the form."""

    client.force_login(user)
    response = client.get(reverse("properties:new"))
    assert response.status_code == 200

    form_data = {
        "user": user,
        "name": "Test House",
        "price": 100000,
        "is_published": True,
        "description": "Test description",
        "full_address": "Test address",
        "phone_number": "+92-3001234567",
        "cnic": "12345-1234567-1",
        "property_type": Property.PropertyType.HOUSE,
    }

    response = client.post(reverse("properties:new"), data=form_data)
    assert (
        response.status_code == 302
    )  # should redirect after successful form submission

    # Check if the property was added
    assert Property.objects.filter(name="Test House").exists()


@pytest.mark.django_db
def test_property_edit_form(user, client):
    """Test editing an existing property using the form."""

    client.force_login(user)
    prop = Property.objects.create(
        user=user,
        name="Test House",
        description="Test description",
        full_address="Test address",
        phone_number="+92-3001234567",
        cnic="12345-1234567-1",
        property_type=Property.PropertyType.HOUSE,
        price=100000,
        is_published=True,
    )
    response = client.get(reverse("properties:edit", args=[prop.id]))
    assert response.status_code == 200

    form_data = {
        "user": user,
        "name": "Test House 2",
        "price": 200000,
        "is_published": True,
        "description": "Test description 2",
        "full_address": "Test address 2",
        "phone_number": "+92-3001234567",
        "cnic": "12345-1234567-1",
        "property_type": Property.PropertyType.HOUSE,
    }

    response = client.post(reverse("properties:edit", args=[prop.id]), data=form_data)
    assert (
        response.status_code == 302
    )  # should redirect after successful form submission

    # Check if the property was edited
    prop.refresh_from_db()
    assert prop.name == "Test House 2"
    assert prop.price == 200000
    assert prop.description == "Test description 2"
    assert prop.full_address == "Test address 2"
    assert prop.phone_number == "+92-3001234567"
    assert prop.cnic == "12345-1234567-1"
    assert prop.property_type == Property.PropertyType.HOUSE
    assert prop.is_published
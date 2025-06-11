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
        name="Test House",
        user=user,
        price=100000,
        is_published=True,
        description="Test description",
        address="Test address",
    )
    assert str(prop) == "Test House"


@pytest.mark.django_db
def test_property_add_form(user, client):
    """Test adding a new property using the form."""

    client.force_login(user)
    response = client.get(reverse("properties:new"))
    assert response.status_code == 200

    form_data = {
        "name": "Test House",
        "price": 100000,
        "is_published": True,
        "description": "Test description",
        "address": "Test address",
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
        name="Test House",
        user=user,
        price=100000,
        is_published=True,
        description="Test description",
        address="Test address",
    )
    response = client.get(reverse("properties:edit", args=[prop.id]))
    assert response.status_code == 200

    form_data = {
        "name": "Test House 2",
        "price": 200000,
        "is_published": True,
        "description": "Test description 2",
        "address": "Test address 2",
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
    assert prop.address == "Test address 2"

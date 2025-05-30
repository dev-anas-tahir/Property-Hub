"""
This module contains test cases for user-related views within the Property Hub application.
It uses pytest and django pytest plugins for testing.
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.properties.models import Property

@pytest.mark.django_db
def test_property_str():
    """Test the string representation of the Property model."""
    user = User.objects.create_user(username="john", password="pass1234")
    property = Property.objects.create(
        name="Test House",
        user=user,
        price=100000,
        is_published=True,
        description="Test description",
        address="Test address"
    )
    assert str(property) == "Test House"

@pytest.mark.django_db
def test_signup_view(client):
    """Test the user signup view."""
    response = client.get(reverse("users:signup"))
    assert response.status_code == 200

    form_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "testpassword123",
        "password2": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post(reverse("users:signup"), data=form_data)

    if response.status_code != 302:
        print(response.context["form"].errors)

    assert response.status_code == 302
    assert User.objects.filter(username="testuser").exists()

@pytest.mark.django_db
def test_login_view(client):
    """Test the login view with valid credentials."""
    User.objects.create_user(
        username="testuser", email="test@example.com", password="testpassword123"
    )

    response = client.get(reverse("users:login"))
    assert response.status_code == 200

    login_data = {
        "username": "testuser",
        "password": "testpassword123",
    }

    response = client.post(reverse("users:login"), data=login_data)
    assert response.status_code == 302  # should redirect after successful login

    # Confirm user is authenticated
    assert "_auth_user_id" in client.session

@pytest.mark.django_db
def test_logout_view(client):
    """Test the logout view."""
    User.objects.create_user(
        username="testuser", email="test@example.com", password="testpassword123"
    )

    client.login(username="testuser", password="testpassword123")

    response = client.get(reverse("users:logout"))
    assert response.status_code == 302  # should redirect after logout

    # Confirm user is logged out
    assert "_auth_user_id" not in client.session

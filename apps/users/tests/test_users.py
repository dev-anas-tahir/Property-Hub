"""
This module contains test cases for user-related views within the Property Hub application.
It uses pytest and django pytest plugins for testing.
"""

import pytest
from django.urls import reverse
from apps.properties.models import Property

# Note: we now rely on the `user` and `user_factory` fixtures from conftest.py


@pytest.mark.django_db
def test_custom_user(user_factory):
    """Test creating a custom user using the user_factory."""

    user = user_factory(username="alice")
    assert user.username == "alice"
    assert user.check_password("password123")


@pytest.mark.django_db
def test_property_str(user):
    """Test the string representation of the Property model."""

    # use the `user` fixture for ownership
    prop = Property.objects.create(
        user=user,
        name="Test House",  
        price=100000,
        is_published=True,
        description="Test description",
        full_address="Test address",
        phone_number="+92-3001234567",
        cnic="12345-1234567-1",
        property_type=Property.PropertyType.HOUSE,
    )
    assert str(prop) == "Test House"


@pytest.mark.django_db
def test_signup_view(client):
    """Test the user signup view."""
    # Get the signup page to get the CSRF token
    response = client.get(reverse("users:signup"))
    assert response.status_code == 200
    
    # Get the CSRF token from the response
    csrf_token = response.cookies['csrftoken'].value
    
    form_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "Testpass123!",  # Ensure it meets password requirements
        "password2": "Testpass123!",  # Ensure it meets password requirements
        "first_name": "Test",
        "last_name": "User",
        "csrfmiddlewaretoken": csrf_token,
    }

    # Make the POST request with the CSRF token
    response = client.post(
        reverse("users:signup"),
        data=form_data,
        follow=True,
        headers={"X-CSRFToken": csrf_token}
    )
    
    # Check for successful redirect (302) or successful render (200)
    assert response.status_code in [200, 302], \
        f"Expected 200 or 302 status, got {response.status_code}. Errors: {getattr(response, 'context', {}).get('form', {}).errors if hasattr(response, 'context') else 'No form in context'}"
    
    # Verify the user was created in the database
    from django.contrib.auth import get_user_model
    User = get_user_model()
    assert User.objects.filter(username="testuser").exists(), \
        "User was not created in the database"


@pytest.mark.django_db
def test_login_view(client, user_factory):
    """Test the login view with valid credentials."""

    # create a user with known credentials
    user_factory(username="loginuser", password="mypassword123")

    response = client.get(reverse("users:login"))
    assert response.status_code == 200

    login_data = {
        "username": "loginuser",
        "password": "mypassword123",
    }

    response = client.post(reverse("users:login"), data=login_data)
    assert response.status_code == 302, (
        f"Login failed with errors: {response.context['form'].errors}"
    )

    # Confirm user is authenticated
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_logout_view(client, user_factory):
    """Test the logout view."""

    user = user_factory(username="logoutuser", password="mypassword123")

    client.force_login(user)
    response = client.get(reverse("users:logout"))
    assert response.status_code == 302

    # Confirm user is logged out
    assert "_auth_user_id" not in client.session

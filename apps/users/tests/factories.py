"""
This module contains test factories for user-related models within the Property Hub application.
"""

from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from factory import Faker, Sequence, LazyAttribute, PostGenerationMethodCall

class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    username = Sequence(lambda n: f"user{n}")
    email = LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    password = PostGenerationMethodCall("set_password", "password123")

    class Meta:
        model = User
        django_get_or_create = ("username",)

# conftest.py
from pytest_factoryboy import register
from apps.users.tests.factories import UserFactory

register(UserFactory)

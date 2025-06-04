import pytest
from apps.users.tests.factories import UserFactory

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def user(db, user_factory):
    return user_factory()

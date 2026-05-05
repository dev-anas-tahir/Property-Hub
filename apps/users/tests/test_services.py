from django.test import TestCase

from apps.shared.exceptions import ApplicationError
from apps.shared.tests.factories import UserFactory
from apps.users.services import user_create, user_update


class UserCreateTests(TestCase):
    def test_creates_user(self):
        user = user_create(
            email="new@example.com",
            password="StrongPass1!",
            first_name="Jane",
            last_name="Doe",
        )
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.first_name, "Jane")

    def test_normalises_email(self):
        user = user_create(
            email="  UPPER@EXAMPLE.COM  ",
            password="StrongPass1!",
            first_name="Jane",
            last_name="Doe",
        )
        self.assertEqual(user.email, "upper@example.com")

    def test_raises_on_duplicate_email(self):
        UserFactory(email="taken@example.com")
        with self.assertRaises(ApplicationError):
            user_create(
                email="taken@example.com",
                password="StrongPass1!",
                first_name="Jane",
                last_name="Doe",
            )

    def test_raises_on_weak_password(self):
        with self.assertRaises(ApplicationError):
            user_create(
                email="weak@example.com",
                password="password",
                first_name="Jane",
                last_name="Doe",
            )


class UserUpdateTests(TestCase):
    def test_updates_profile(self):
        user = UserFactory(first_name="Old", last_name="Name", email="old@example.com")
        updated = user_update(
            user=user,
            first_name="New",
            last_name="Name",
            email="new@example.com",
        )
        self.assertEqual(updated.first_name, "New")
        self.assertEqual(updated.email, "new@example.com")

    def test_raises_on_taken_email(self):
        UserFactory(email="taken@example.com")
        user = UserFactory(email="mine@example.com")
        with self.assertRaises(ApplicationError):
            user_update(
                user=user,
                first_name="Jane",
                last_name="Doe",
                email="taken@example.com",
            )

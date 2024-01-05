"""
Test Models
"""

import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from core import models  # noqa


def create_user(email='test_user2@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """ Test models."""

    def setUp(self) -> None:
        self.email = "test_user1@example.com"
        self.password = "testpass123"

        self.user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password,
        )

    def test_create_user_with_email_and_password_successful(self):
        """ Test creating a user with an email and password is successful."""
        self.assertEqual(self.user.email, self.email)
        self.assertTrue(self.user.check_password(self.password))
        self.assertTrue(self.user.is_ambassador)

        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_superuser)

    def test_creating_with_first_name_and_last_name_have_fullname(self):
        """Test that the full name attr is created after creating a user."""
        first_name = "First"
        last_name = "Last"
        email = "test4@example.com",
        user, created = get_user_model().objects.get_or_create(
            email=email,
            password="password123",
            first_name=first_name,
            last_name=last_name,
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, f"{first_name} {last_name}")

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Tests that creating a new user without an email
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_new_user_without_password_raises_error(self):
        """Tests that creating a new user without a password
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("user@example.com", "")

    def test_create_superuser(self):
        """ Test creating a superuser."""

        super_user = get_user_model().objects.create_superuser(
            email="super_user@example.com",
            password="password123",
        )
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_admin)
        self.assertFalse(super_user.is_ambassador)
        self.assertTrue(super_user.is_staff)

    def test_create_token(self):
        """ Test creating a token for a user is successful."""
        token = uuid.uuid4().hex

        models.UserToken.objects.create(
            user=self.user,
            token=token,
            expired_at=timezone.now()

        )

        auth = self.user.auth
        self.assertEqual(auth.token, token)

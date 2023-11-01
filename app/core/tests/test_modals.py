"""TEST FOR MODALS"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal


class ModalTests(TestCase):
    """Test Models"""

    def test_create_user_with_email_and_password(self):
        """Test creating user with an email & password"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_when_registration(self):
        """Test new user without email raise when registration"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_super_user(self):
        """Test create super user"""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample receipe description.",
        )

        self.assertEqual(str(recipe), recipe.title)

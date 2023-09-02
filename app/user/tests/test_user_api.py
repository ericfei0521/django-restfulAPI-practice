"""Tests for the user API"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")


class PublicUserAPITests(TestCase):
    """Test the public features of the user API"""

    normal_payload = {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test Name",
    }
    short_password_payload = {
        "email": "test@example.com",
        "password": "test",
        "name": "Test Name",
    }

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successfully(self):
        """Test succesfully create a new user"""
        res = self.client.post(CREATE_USER_URL, self.normal_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.normal_payload["email"])
        self.assertTrue(user.check_password(self.normal_payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        get_user_model().objects.create_user(**self.normal_payload)
        res = self.client.post(CREATE_USER_URL, self.normal_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 8 chars."""
        res = self.client.post(CREATE_USER_URL, self.short_password_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model()
            .objects.filter(email=self.short_password_payload["email"])
            .exists()
        )
        self.assertFalse(user_exists)

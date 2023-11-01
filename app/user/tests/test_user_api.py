"""Tests for the user API"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:login")
UPDATE_URL = reverse("user:update")
USERS_URL = reverse("user:users")


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

    def test_create_token_for_user(self):
        """Test genreates token for valid user"""
        get_user_model().objects.create_user(**self.normal_payload)
        payload = {
            "email": self.normal_payload["email"],
            "password": self.normal_payload["password"],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test return error if credentials invalid"""
        get_user_model().objects.create_user(
            email=self.normal_payload["email"], password=self.normal_payload["password"]
        )
        payload = {"email": self.normal_payload["email"], "password": "badpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_passowrd(self):
        """Test post a blank password returns an error"""
        payload = {"email": self.normal_payload["email"], "password": ""}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.get(UPDATE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="testpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(UPDATE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "name": self.user.name,
                "email": self.user.email,
            },
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(UPDATE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {"name": "Updated name", "password": "newpassword123"}

        res = self.client.patch(UPDATE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_user_list(self):
        """Test get users list"""
        res = self.client.get(USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print("resData", res.data)
        self.assertEqual(
            res.data,
            [
                {
                    "name": self.user.name,
                    "email": self.user.email,
                },
            ],
        )

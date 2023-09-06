from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

REGISTER_USER_URL = reverse("api:register")
TOKEN_CREATE_URL = reverse("api:token_create")
USER_CURRENCY = reverse("api:user_currency")
CURRENCY_RATES = reverse("api:currency_rates")
CURRENCY_ANALYTICS = reverse("api:currency_analytics", args=(1,))


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {"email": "test@gmail.com", "password": "12345678i"}
        res = self.client.post(REGISTER_USER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=res.data['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {"email": "test@gmail.com", "password": "12345678i"}
        create_user(**payload)

        # creating user with API using same credentials
        res = self.client.post(REGISTER_USER_URL, payload, format="json")
        self.assertIn("email", res.data)  # есть ли поле `email` с ответом об ошибке
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 8 characters. This is default 8 character limit by Django."""
        payload = {"email": "test@gmail.com", "password": "pw"}
        res = self.client.post(REGISTER_USER_URL, payload, format="json")
        self.assertIn("password", res.data)  # есть ли поле `password` с ответом об ошибке
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {"email": "test@gmail.com", "password": "12345678i"}
        create_user(**payload)

        res = self.client.post(TOKEN_CREATE_URL, payload, format="json")
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email="test@admin.com", password="testpass")
        payload = {"email": "test@admin.com", "password": "testfail"}
        res = self.client.post(TOKEN_CREATE_URL, payload, format="json")
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {"email": "test@admin.com", "password": "testpass"}
        res = self.client.post(TOKEN_CREATE_URL, payload, format="json")
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_fields(self):
        """Test that email and password are required"""
        payload = {"email": "test", "password": ""}
        res = self.client.post(TOKEN_CREATE_URL, payload, format="json")
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        payload = {"email": "test@gmail.com", "password": "12345678i"}
        self.user = create_user(**payload)
        self.client = APIClient()
        res = self.client.post(TOKEN_CREATE_URL, {"email": "test@gmail.com", "password": "12345678i"}, format="json")
        self.access_token = res.data["access"]
        self.refresh_token = res.data["refresh"]

    def test_inactive_user_api_jwt_token(self):
        """Test that inactive user is not able to get an access token"""
        payload = {"email": "test@gmail.com", "password": "12345678i"}
        self.user.is_active = False
        self.user.save()
        res = self.client.post(TOKEN_CREATE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_valid_user_currency_threshold(self):
        """Test creating user currency with valid payload is successful"""
        payload = {"currency": "R01020A", "threshold": 50.8352}
        self.client.force_authenticate(user=self.user)
        res = self.client.post(USER_CURRENCY, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('currency', res.data)
        self.assertIn('threshold', res.data)

    def test_create_invalid_user_currency_threshold(self):
        """Test creating user currency with invalid payload is fail"""
        payload = {"currency": "R01020A1234", "threshold": 0}
        self.client.force_authenticate(user=self.user)
        res = self.client.post(USER_CURRENCY, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthorized_user_currency_threshold(self):
        """Test not creating user currency unauthorized user"""
        payload = {"currency": "R01020A", "threshold": 50.8352}
        res = self.client.post(USER_CURRENCY, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@gmail.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized
        - after @ email domain should be made lower case."""
        email = "test@GMAIL.COM"
        password = "TestPass123"
        user = get_user_model().objects.create_user(email, password)
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "TestPass123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            "test@gmail.com",
            "TestPass123"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

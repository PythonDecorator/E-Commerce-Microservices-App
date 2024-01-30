"""
Tests for the user API.
"""
from django.http import SimpleCookie
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import UserToken  # noqa

from core.authentication import JWTAuthentication  # noqa

CREATE_USER_URL = reverse('user:register')
LOGIN_URL = reverse('user:login')
LOGOUT_URL = reverse('user:logout')
PROFILE_URL = reverse('user:me')
USERS_URL = reverse('user:users')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'first_name': "testpass123",
            'last_name': "testpass123",
            'email': 'test@example.com',
            'password': "testpass123",
            'password1': "testpass123",
        }

    def tearDown(self) -> None:
        self.payload = {
            'first_name': "testpass123",
            'last_name': "testpass123",
            'email': 'test@example.com',
            'password': "testpass123",
            'password1': "testpass123",
        }

    def test_create_user_success(self):
        """Test creating a user is successful."""

        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=self.payload['email'])

        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', res.data)
        self.assertTrue(user.is_ambassador)

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email exists."""
        create_user(email=self.payload["email"], password=self.payload["password"])

        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        self.payload["password"] = "short"
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=self.payload['email']).exists()
        self.assertFalse(user_exists)

    def test_ambassador_login_user(self):
        """Test ambassador login with valid credentials."""
        user_details = {
            'email': 'test@example.com',
            'password': "password123",
        }

        user = create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
            'scope': "ambassador",
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', res.data)

        self.assertEqual(user.auth.token, res.data["jwt"])

    # def test_logging_again_when_logged_in_not_allowed(self):
    #     """Test trying to login when still logged-in returns forbidden error."""
    #     payload = {'email': 'test@example.com', 'password': 'password123'}
    #     user = create_user(**payload)
    #
    #     payload["scope"] = "ambassador"
    #
    #     res1 = self.client.post(LOGIN_URL, payload)
    #     self.assertEqual(res1.status_code, status.HTTP_200_OK)
    #
    #     res2 = self.client.post(LOGIN_URL, payload)
    #     self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)
    #     self.assertEqual(user.auth.token, res1.data["jwt"])
    #
    #     self.assertNotIn(user.auth.token, res2.data)

    def test_ambassador_login_email_not_found(self):
        """Test error returned if user not found for given email."""

        payload = {'email': 'test@example.com',
                   'password': 'pass123',
                   "scope": "ambassador"}
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('jwt', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ambassador_login_with_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='good-pass')

        payload = {'email': 'test@example.com',
                   'password': 'bad-pass',
                   "scope": "ambassador"
                   }
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('jwt', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ambassador_login_with_blank_password(self):
        """Test posting a blank password returns error"""
        payload = {'email': 'test@example.com',
                   'password': '',
                   "scope": "ambassador"
                   }
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('jwt', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
        )

        token = JWTAuthentication.generate_jwt(self.user.id, "ambassador")
        cookies = SimpleCookie()
        cookies["jwt"] = token

        self.client = APIClient(HTTP_COOKIE=cookies.output(header='', sep='; '))
        self.client.force_login(self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "id": self.user.id,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the ME endpoint."""
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'first_name': 'updated first name',
                   'last_name': 'updated last name',
                   'password': 'newpassword123'
                   }

        res = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertEqual(self.user.last_name, payload['last_name'])
        self.assertEqual(self.user.name, f"{payload['first_name']} {payload['last_name']}")
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_cannot_updated_their_email(self):
        """Test updating the user email is not allowed."""
        payload = {'email': 'new@example.com'}

        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, payload['email'])

    def test_getting_all_the_users(self):
        """Test retrieving all users."""

        create_user(email="user2@example.com", password="user1234")
        create_user(email="user3@example.com", password="user1234")
        create_user(email="user4@example.com", password="user1234")

        res = self.client.get(USERS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        users = get_user_model().objects.all()

        self.assertEqual(len(res.data), 4)
        self.assertEqual(len(res.data), len(users))
        self.assertNotIn("password", res.data)

    def test_logout(self):
        """Test logout"""
        res = self.client.post(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(UserToken.objects.filter(user=self.user).exists())

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthAPITests(APITestCase):

    REGISTER_URL = "/api/auth/register/"
    LOGIN_URL = "/api/auth/login/"
    LOGOUT_URL = "/api/auth/logout/"
    ME_URL = "/api/auth/me/"

    def setUp(self):
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

    def test_register_user_successfully(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "AnotherStrongPassword123!",
            "password_confirm": "AnotherStrongPassword123!",
        }

        response = self.client.post(
            self.REGISTER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                username="newuser"
            ).exists()
        )

        created_user = User.objects.get(
            username="newuser"
        )

        self.assertEqual(
            created_user.email,
            "newuser@example.com",
        )

        self.assertTrue(
            created_user.check_password(
                "AnotherStrongPassword123!"
            )
        )

    def test_register_with_existing_username_fails(self):
        payload = {
            "username": self.username,
            "email": "another@example.com",
            "password": "AnotherStrongPassword123!",
            "password_confirm": "AnotherStrongPassword123!",
        }

        response = self.client.post(
            self.REGISTER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            User.objects.filter(
                username=self.username
            ).count(),
            1,
        )

    def test_register_with_mismatched_passwords_fails(self):
        payload = {
            "username": "differentuser",
            "email": "different@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "WrongPassword123!",
        }

        response = self.client.post(
            self.REGISTER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User.objects.filter(
                username="differentuser"
            ).exists()
        )

    def test_login_successfully(self):
        payload = {
            "username": self.username,
            "password": self.password,
        }

        response = self.client.post(
            self.LOGIN_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )

        self.assertEqual(
            int(
                self.client.session[
                    "_auth_user_id"
                ]
            ),
            self.user.id,
        )

    def test_login_with_wrong_password_fails(self):
        payload = {
            "username": self.username,
            "password": "WrongPassword123!",
        }

        response = self.client.post(
            self.LOGIN_URL,
            payload,
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
            ],
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_me_returns_logged_in_user(self):
        self.client.force_login(
            self.user
        )

        response = self.client.get(
            self.ME_URL
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            self.username,
        )

        self.assertEqual(
            response.data["email"],
            self.email,
        )

    def test_me_requires_authentication(self):
        response = self.client.get(
            self.ME_URL
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_logout_user(self):
        self.client.force_login(
            self.user
        )

        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )

        response = self.client.post(
            self.LOGOUT_URL,
            {},
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
            ],
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )
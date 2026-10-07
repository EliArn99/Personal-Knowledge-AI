from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Chat


User = get_user_model()


class ChatAPITests(APITestCase):

    CHATS_URL = "/api/chats/"

    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            username="chatuser",
            email="chatuser@example.com",
            password=self.password,
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password=self.password,
        )

        self.client.force_login(
            self.user
        )

    def detail_url(self, chat_id):
        return f"/api/chats/{chat_id}/"

    def test_create_chat_successfully(self):
        payload = {
            "title": "My First Chat",
        }

        response = self.client.post(
            self.CHATS_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Chat.objects.count(),
            1,
        )

        chat = Chat.objects.get()

        self.assertEqual(
            chat.title,
            "My First Chat",
        )

        self.assertEqual(
            chat.user,
            self.user,
        )

    def test_create_chat_assigns_authenticated_user(self):
        payload = {
            "title": "Owned Chat",
        }

        response = self.client.post(
            self.CHATS_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        chat = Chat.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            chat.user,
            self.user,
        )

    def test_list_returns_only_current_users_chats(self):
        own_chat_1 = Chat.objects.create(
            user=self.user,
            title="My Chat 1",
        )

        own_chat_2 = Chat.objects.create(
            user=self.user,
            title="My Chat 2",
        )

        Chat.objects.create(
            user=self.other_user,
            title="Other User Chat",
        )

        response = self.client.get(
            self.CHATS_URL
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            chat["id"]
            for chat in response.data
        }

        self.assertEqual(
            returned_ids,
            {
                own_chat_1.id,
                own_chat_2.id,
            },
        )

    def test_retrieve_own_chat(self):
        chat = Chat.objects.create(
            user=self.user,
            title="My Chat",
        )

        response = self.client.get(
            self.detail_url(chat.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            chat.id,
        )

        self.assertEqual(
            response.data["title"],
            "My Chat",
        )

    def test_update_chat_title(self):
        chat = Chat.objects.create(
            user=self.user,
            title="Old Title",
        )

        payload = {
            "title": "New Title",
        }

        response = self.client.patch(
            self.detail_url(chat.id),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        chat.refresh_from_db()

        self.assertEqual(
            chat.title,
            "New Title",
        )

    def test_delete_chat(self):
        chat = Chat.objects.create(
            user=self.user,
            title="Delete Me",
        )

        response = self.client.delete(
            self.detail_url(chat.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Chat.objects.filter(
                id=chat.id
            ).exists()
        )

    def test_cannot_access_another_users_chat(self):
        other_chat = Chat.objects.create(
            user=self.other_user,
            title="Private Chat",
        )

        response = self.client.get(
            self.detail_url(
                other_chat.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_update_another_users_chat(self):
        other_chat = Chat.objects.create(
            user=self.other_user,
            title="Private Chat",
        )

        response = self.client.patch(
            self.detail_url(
                other_chat.id
            ),
            {
                "title": "Hacked Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        other_chat.refresh_from_db()

        self.assertEqual(
            other_chat.title,
            "Private Chat",
        )

    def test_cannot_delete_another_users_chat(self):
        other_chat = Chat.objects.create(
            user=self.other_user,
            title="Private Chat",
        )

        response = self.client.delete(
            self.detail_url(
                other_chat.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Chat.objects.filter(
                id=other_chat.id
            ).exists()
        )

    def test_anonymous_user_cannot_list_chats(self):
        self.client.logout()

        response = self.client.get(
            self.CHATS_URL
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_anonymous_user_cannot_create_chat(self):
        self.client.logout()

        response = self.client.post(
            self.CHATS_URL,
            {
                "title": "Anonymous Chat",
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

        self.assertFalse(
            Chat.objects.filter(
                title="Anonymous Chat"
            ).exists()
        )

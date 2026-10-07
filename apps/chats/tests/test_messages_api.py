from unittest.mock import patch

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from apps.chats.models import Chat, Message

User = get_user_model()


class ChatMessageAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="messageuser",
            email="messageuser@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPassword123!",
        )

        self.chat = Chat.objects.create(
            user=self.user,
            title="Test Chat",
        )

        self.client.force_login(
            self.user
        )

    def messages_url(self, chat_id=None):
        chat_id = chat_id or self.chat.id

        return (
            f"/api/chats/{chat_id}/messages/"
        )

    def test_list_messages_for_own_chat(self):
        Message.objects.create(
            chat=self.chat,
            role=Message.Role.USER,
            content="Hello",
        )

        Message.objects.create(
            chat=self.chat,
            role=Message.Role.ASSISTANT,
            content="Hi there",
        )

        response = self.client.get(
            self.messages_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertEqual(
            response.data[0]["role"],
            Message.Role.USER,
        )

        self.assertEqual(
            response.data[0]["content"],
            "Hello",
        )

        self.assertEqual(
            response.data[1]["role"],
            Message.Role.ASSISTANT,
        )

        self.assertEqual(
            response.data[1]["content"],
            "Hi there",
        )

    @patch(
        "apps.chats.views.generate_chat_response"
    )
    @patch(
        "apps.chats.views.answer_with_documents"
    )
    def test_create_message_uses_rag_when_sources_exist(
        self,
        mock_answer_with_documents,
        mock_generate_chat_response,
    ):
        mock_answer_with_documents.return_value = {
            "answer": (
                "Django REST Framework is a toolkit "
                "for building APIs."
            ),
            "sources": [
                {
                    "document_id": 1,
                    "document_title": "Django Notes",
                    "chunk_index": 0,
                    "score": 0.91,
                }
            ],
        }

        response = self.client.post(
            self.messages_url(),
            {
                "content":
                    "What is Django REST Framework?"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Message.objects.filter(
                chat=self.chat
            ).count(),
            2,
        )

        user_message = Message.objects.get(
            chat=self.chat,
            role=Message.Role.USER,
        )

        assistant_message = Message.objects.get(
            chat=self.chat,
            role=Message.Role.ASSISTANT,
        )

        self.assertEqual(
            user_message.content,
            "What is Django REST Framework?",
        )

        self.assertEqual(
            assistant_message.content,
            (
                "Django REST Framework is a toolkit "
                "for building APIs."
            ),
        )

        self.assertEqual(
            len(assistant_message.sources),
            1,
        )

        self.assertEqual(
            assistant_message.sources[0][
                "document_title"
            ],
            "Django Notes",
        )

        mock_answer_with_documents.assert_called_once()

        mock_generate_chat_response.assert_not_called()

    @patch(
        "apps.chats.views.generate_chat_response"
    )
    @patch(
        "apps.chats.views.answer_with_documents"
    )
    def test_create_message_falls_back_when_no_sources(
        self,
        mock_answer_with_documents,
        mock_generate_chat_response,
    ):
        mock_answer_with_documents.return_value = {
            "answer": None,
            "sources": [],
        }

        mock_generate_chat_response.return_value = (
            "Here are three dinner ideas."
        )

        response = self.client.post(
            self.messages_url(),
            {
                "content":
                    "Give me three dinner ideas."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        assistant_message = Message.objects.get(
            chat=self.chat,
            role=Message.Role.ASSISTANT,
        )

        self.assertEqual(
            assistant_message.content,
            "Here are three dinner ideas.",
        )

        self.assertEqual(
            assistant_message.sources,
            [],
        )

        mock_answer_with_documents.assert_called_once()

        mock_generate_chat_response.assert_called_once()

    @patch(
        "apps.chats.views.generate_chat_response"
    )
    @patch(
        "apps.chats.views.answer_with_documents"
    )
    def test_response_contains_user_and_assistant_messages(
        self,
        mock_answer_with_documents,
        mock_generate_chat_response,
    ):
        mock_answer_with_documents.return_value = {
            "answer": None,
            "sources": [],
        }

        mock_generate_chat_response.return_value = (
            "Mock AI response"
        )

        response = self.client.post(
            self.messages_url(),
            {
                "content": "Hello AI"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "user_message",
            response.data,
        )

        self.assertIn(
            "assistant_message",
            response.data,
        )

        self.assertEqual(
            response.data[
                "user_message"
            ]["role"],
            Message.Role.USER,
        )

        self.assertEqual(
            response.data[
                "assistant_message"
            ]["role"],
            Message.Role.ASSISTANT,
        )

        self.assertEqual(
            response.data[
                "assistant_message"
            ]["content"],
            "Mock AI response",
        )

    def test_cannot_access_other_users_messages(self):
        other_chat = Chat.objects.create(
            user=self.other_user,
            title="Private Chat",
        )

        Message.objects.create(
            chat=other_chat,
            role=Message.Role.USER,
            content="Private message",
        )

        response = self.client.get(
            self.messages_url(
                other_chat.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    @patch(
        "apps.chats.views.generate_chat_response"
    )
    @patch(
        "apps.chats.views.answer_with_documents"
    )
    def test_cannot_post_message_to_other_users_chat(
        self,
        mock_answer_with_documents,
        mock_generate_chat_response,
    ):
        other_chat = Chat.objects.create(
            user=self.other_user,
            title="Private Chat",
        )

        response = self.client.post(
            self.messages_url(
                other_chat.id
            ),
            {
                "content": "Unauthorized message"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            Message.objects.filter(
                chat=other_chat,
                content="Unauthorized message",
            ).exists()
        )

        mock_answer_with_documents.assert_not_called()

        mock_generate_chat_response.assert_not_called()

    def test_anonymous_user_cannot_list_messages(self):
        self.client.logout()

        response = self.client.get(
            self.messages_url()
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_anonymous_user_cannot_create_message(self):
        self.client.logout()

        response = self.client.post(
            self.messages_url(),
            {
                "content": "Anonymous message"
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
            Message.objects.filter(
                content="Anonymous message"
            ).exists()
        )

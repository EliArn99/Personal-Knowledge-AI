from unittest.mock import patch

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai.services.rag_service import RAGServiceError


User = get_user_model()


class DocumentRAGAPITests(APITestCase):

    ASK_URL = "/api/documents/ask/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="raguser",
            email="raguser@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(
            self.user
        )

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_ask_returns_rag_answer_and_sources(
        self,
        mock_answer_with_documents,
    ):
        mock_answer_with_documents.return_value = {
            "answer": (
                "Django REST Framework is used "
                "for building web APIs."
            ),
            "sources": [
                {
                    "document_id": 1,
                    "document_title": "Django Notes",
                    "chunk_index": 0,
                    "score": 0.91,
                    "content": (
                        "Django REST Framework "
                        "helps build APIs."
                    ),
                }
            ],
        }

        response = self.client.post(
            self.ASK_URL,
            {
                "question": (
                    "What is Django REST Framework?"
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["answer"],
            (
                "Django REST Framework is used "
                "for building web APIs."
            ),
        )

        self.assertEqual(
            len(response.data["sources"]),
            1,
        )

        self.assertEqual(
            response.data["sources"][0][
                "document_title"
            ],
            "Django Notes",
        )

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_ask_uses_default_limit_and_min_score(
        self,
        mock_answer_with_documents,
    ):
        mock_answer_with_documents.return_value = {
            "answer": "Mock answer",
            "sources": [],
        }

        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Explain Django"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mock_answer_with_documents.assert_called_once_with(
            user=self.user,
            question="Explain Django",
            limit=5,
            min_score=0.30,
        )

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_ask_uses_custom_limit_and_min_score(
        self,
        mock_answer_with_documents,
    ):
        mock_answer_with_documents.return_value = {
            "answer": "Mock answer",
            "sources": [],
        }

        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Explain embeddings",
                "limit": 10,
                "min_score": 0.55,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mock_answer_with_documents.assert_called_once_with(
            user=self.user,
            question="Explain embeddings",
            limit=10,
            min_score=0.55,
        )

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_empty_question_is_rejected(
        self,
        mock_answer_with_documents,
    ):
        response = self.client.post(
            self.ASK_URL,
            {
                "question": ""
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_answer_with_documents.assert_not_called()

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_missing_question_is_rejected(
        self,
        mock_answer_with_documents,
    ):
        response = self.client.post(
            self.ASK_URL,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_answer_with_documents.assert_not_called()

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_limit_below_minimum_is_rejected(
        self,
        mock_answer_with_documents,
    ):
        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Test question",
                "limit": 0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_answer_with_documents.assert_not_called()

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_limit_above_maximum_is_rejected(
        self,
        mock_answer_with_documents,
    ):
        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Test question",
                "limit": 21,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_answer_with_documents.assert_not_called()

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_min_score_below_minimum_is_rejected(
        self,
        mock_answer_with_documents,
    ):
        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Test question",
                "min_score": -1.1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_answer_with_documents.assert_not_called()

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_min_score_above_maximum_is_rejected(
        self,
        mock_answer_with_documents,
    ):
        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Test question",
                "min_score": 1.1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_answer_with_documents.assert_not_called()

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_rag_service_error_returns_500(
        self,
        mock_answer_with_documents,
    ):
        mock_answer_with_documents.side_effect = (
            RAGServiceError(
                "RAG service failed."
            )
        )

        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Explain Django"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        self.assertEqual(
            response.data["detail"],
            "RAG service failed.",
        )

    @patch(
        "apps.documents.views.answer_with_documents"
    )
    def test_anonymous_user_cannot_use_ask_endpoint(
        self,
        mock_answer_with_documents,
    ):
        self.client.logout()

        response = self.client.post(
            self.ASK_URL,
            {
                "question": "Explain Django"
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

        mock_answer_with_documents.assert_not_called()

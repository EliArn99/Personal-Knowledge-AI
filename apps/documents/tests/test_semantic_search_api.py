from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from apps.documents.models import Document, DocumentChunk


User = get_user_model()


class DocumentSemanticSearchAPITests(APITestCase):

    SEARCH_URL = "/api/documents/search/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="searchuser",
            email="searchuser@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="othersearchuser",
            email="othersearchuser@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(
            self.user
        )

        uploaded_file = SimpleUploadedFile(
            "django.txt",
            b"Django document",
            content_type="text/plain",
        )

        self.document = Document.objects.create(
            user=self.user,
            title="Django Notes",
            file=uploaded_file,
            original_filename="django.txt",
            file_type="txt",
            file_size=15,
        )

        self.chunk = DocumentChunk.objects.create(
            document=self.document,
            chunk_index=0,
            content=(
                "Django REST Framework is used "
                "for building APIs."
            ),
            embedding=[0.1, 0.2, 0.3],
            embedding_model="test-model",
        )

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_semantic_search_returns_results(
        self,
        mock_semantic_search,
    ):
        mock_semantic_search.return_value = [
            {
                "chunk": self.chunk,
                "score": 0.91234567,
            }
        ]

        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": "What is DRF?"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["query"],
            "What is DRF?",
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        result = response.data["results"][0]

        self.assertEqual(
            result["document_id"],
            self.document.id,
        )

        self.assertEqual(
            result["document_title"],
            "Django Notes",
        )

        self.assertEqual(
            result["chunk_index"],
            0,
        )

        self.assertEqual(
            result["content"],
            (
                "Django REST Framework is used "
                "for building APIs."
            ),
        )

        self.assertEqual(
            result["score"],
            0.912346,
        )

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_semantic_search_passes_current_user(
        self,
        mock_semantic_search,
    ):
        mock_semantic_search.return_value = []

        self.client.post(
            self.SEARCH_URL,
            {
                "query": "Django"
            },
            format="json",
        )

        mock_semantic_search.assert_called_once_with(
            user=self.user,
            query="Django",
            limit=5,
        )

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_semantic_search_uses_custom_limit(
        self,
        mock_semantic_search,
    ):
        mock_semantic_search.return_value = []

        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": "Django",
                "limit": 10,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mock_semantic_search.assert_called_once_with(
            user=self.user,
            query="Django",
            limit=10,
        )

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_semantic_search_returns_empty_results(
        self,
        mock_semantic_search,
    ):
        mock_semantic_search.return_value = []

        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": "Something unrelated"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

        self.assertEqual(
            response.data["results"],
            [],
        )

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_empty_query_is_rejected(
        self,
        mock_semantic_search,
    ):
        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": ""
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_semantic_search.assert_not_called()

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_missing_query_is_rejected(
        self,
        mock_semantic_search,
    ):
        response = self.client.post(
            self.SEARCH_URL,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_semantic_search.assert_not_called()

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_limit_below_minimum_is_rejected(
        self,
        mock_semantic_search,
    ):
        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": "Django",
                "limit": 0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_semantic_search.assert_not_called()

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_limit_above_maximum_is_rejected(
        self,
        mock_semantic_search,
    ):
        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": "Django",
                "limit": 21,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_semantic_search.assert_not_called()

    @patch(
        "apps.documents.views.semantic_search"
    )
    def test_anonymous_user_cannot_search(
        self,
        mock_semantic_search,
    ):
        self.client.logout()

        response = self.client.post(
            self.SEARCH_URL,
            {
                "query": "Django"
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

        mock_semantic_search.assert_not_called()

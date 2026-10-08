import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from apps.documents.models import Document
from apps.documents.serializers import MAX_FILE_SIZE


User = get_user_model()


class DocumentUploadValidationTests(APITestCase):

    DOCUMENTS_URL = "/api/documents/"

    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()

        self.override = override_settings(
            MEDIA_ROOT=self.temp_media_root
        )
        self.override.enable()

        self.addCleanup(
            self.override.disable
        )

        self.addCleanup(
            shutil.rmtree,
            self.temp_media_root,
            ignore_errors=True,
        )

        self.user = User.objects.create_user(
            username="uploaduser",
            email="uploaduser@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(
            self.user
        )

    def detail_url(self, document_id):
        return (
            f"/api/documents/{document_id}/"
        )

    def make_file(
        self,
        name,
        content=b"Test document content",
        content_type="text/plain",
    ):
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type=content_type,
        )

    @patch(
        "apps.documents.views.process_document_indexing"
    )
    @patch(
        "apps.documents.views.process_document"
    )
    def test_txt_file_is_allowed(
        self,
        mock_process_document,
        mock_process_document_indexing,
    ):
        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": self.make_file(
                    "notes.txt"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Document.objects.filter(
                original_filename="notes.txt"
            ).exists()
        )

    @patch(
        "apps.documents.views.process_document_indexing"
    )
    @patch(
        "apps.documents.views.process_document"
    )
    def test_md_file_is_allowed(
        self,
        mock_process_document,
        mock_process_document_indexing,
    ):
        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": self.make_file(
                    "notes.md",
                    b"# Markdown notes",
                    "text/markdown",
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.file_type,
            "md",
        )

    @patch(
        "apps.documents.views.process_document_indexing"
    )
    @patch(
        "apps.documents.views.process_document"
    )
    def test_pdf_file_is_allowed(
        self,
        mock_process_document,
        mock_process_document_indexing,
    ):
        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": self.make_file(
                    "notes.pdf",
                    b"%PDF-1.4 test content",
                    "application/pdf",
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.file_type,
            "pdf",
        )

    @patch(
        "apps.documents.views.process_document"
    )
    def test_unsupported_file_type_is_rejected(
        self,
        mock_process_document,
    ):
        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": self.make_file(
                    "malware.exe",
                    b"fake exe content",
                    "application/octet-stream",
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

        mock_process_document.assert_not_called()

    @patch(
        "apps.documents.views.process_document"
    )
    def test_empty_file_is_rejected(
        self,
        mock_process_document,
    ):
        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": self.make_file(
                    "empty.txt",
                    b"",
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

        mock_process_document.assert_not_called()

    @patch(
        "apps.documents.views.process_document"
    )
    def test_file_larger_than_10_mb_is_rejected(
        self,
        mock_process_document,
    ):
        oversized_content = (
            b"a" * (MAX_FILE_SIZE + 1)
        )

        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": self.make_file(
                    "large.txt",
                    oversized_content,
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

        mock_process_document.assert_not_called()

    def test_empty_title_is_rejected_on_update(
        self,
    ):
        document = Document.objects.create(
            user=self.user,
            title="Original Title",
            file=self.make_file(
                "notes.txt"
            ),
            original_filename="notes.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.patch(
            self.detail_url(
                document.id
            ),
            {
                "title": "   ",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "title",
            response.data,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.title,
            "Original Title",
        )

    def test_existing_document_file_cannot_be_replaced(
        self,
    ):
        document = Document.objects.create(
            user=self.user,
            title="Original Document",
            file=self.make_file(
                "original.txt"
            ),
            original_filename="original.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.patch(
            self.detail_url(
                document.id
            ),
            {
                "file": self.make_file(
                    "replacement.txt"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.original_filename,
            "original.txt",
        )


import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from apps.documents.models import Document


User = get_user_model()


class DocumentAPITests(APITestCase):

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
            username="documentuser",
            email="documentuser@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(
            self.user
        )

    def detail_url(self, document_id):
        return (
            f"/api/documents/{document_id}/"
        )

    def create_test_file(
        self,
        name="notes.txt",
        content=b"Django REST Framework notes.",
    ):
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type="text/plain",
        )

    @patch(
        "apps.documents.views.process_document_indexing"
    )
    @patch(
        "apps.documents.views.process_document"
    )
    def test_upload_document_successfully(
        self,
        mock_process_document,
        mock_process_document_indexing,
    ):
        test_file = self.create_test_file()

        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "title": "Django Notes",
                "file": test_file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Document.objects.count(),
            1,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.user,
            self.user,
        )

        self.assertEqual(
            document.title,
            "Django Notes",
        )

        self.assertEqual(
            document.original_filename,
            "notes.txt",
        )

        self.assertEqual(
            document.file_type,
            "txt",
        )

        self.assertGreater(
            document.file_size,
            0,
        )

        mock_process_document.assert_called_once_with(
            document
        )

        mock_process_document_indexing.assert_not_called()

    @patch(
        "apps.documents.views.process_document"
    )
    def test_upload_without_title_uses_filename(
        self,
        mock_process_document,
    ):
        test_file = self.create_test_file(
            name="python_notes.txt"
        )

        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "file": test_file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.title,
            "python_notes",
        )

    def test_list_returns_only_current_users_documents(
        self,
    ):
        own_document_1 = Document.objects.create(
            user=self.user,
            title="My Document 1",
            file=self.create_test_file(
                name="one.txt"
            ),
            original_filename="one.txt",
            file_type="txt",
            file_size=10,
        )

        own_document_2 = Document.objects.create(
            user=self.user,
            title="My Document 2",
            file=self.create_test_file(
                name="two.txt"
            ),
            original_filename="two.txt",
            file_type="txt",
            file_size=10,
        )

        Document.objects.create(
            user=self.other_user,
            title="Other User Document",
            file=self.create_test_file(
                name="other.txt"
            ),
            original_filename="other.txt",
            file_type="txt",
            file_size=10,
        )

        response = self.client.get(
            self.DOCUMENTS_URL
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            document["id"]
            for document in response.data
        }

        self.assertEqual(
            returned_ids,
            {
                own_document_1.id,
                own_document_2.id,
            },
        )

    def test_retrieve_own_document(self):
        document = Document.objects.create(
            user=self.user,
            title="My Document",
            file=self.create_test_file(),
            original_filename="notes.txt",
            file_type="txt",
            file_size=100,
            extracted_text="Extracted document text.",
            extraction_status=(
                Document.ExtractionStatus.READY
            ),
        )

        response = self.client.get(
            self.detail_url(
                document.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            document.id,
        )

        self.assertEqual(
            response.data["title"],
            "My Document",
        )

        self.assertEqual(
            response.data["extracted_text"],
            "Extracted document text.",
        )

    def test_rename_document(self):
        document = Document.objects.create(
            user=self.user,
            title="Old Title",
            file=self.create_test_file(),
            original_filename="notes.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.patch(
            self.detail_url(
                document.id
            ),
            {
                "title": "New Title",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.title,
            "New Title",
        )

        self.assertEqual(
            document.original_filename,
            "notes.txt",
        )

    def test_delete_document(self):
        document = Document.objects.create(
            user=self.user,
            title="Delete Me",
            file=self.create_test_file(),
            original_filename="notes.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.delete(
            self.detail_url(
                document.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Document.objects.filter(
                id=document.id
            ).exists()
        )

    def test_cannot_retrieve_other_users_document(
        self,
    ):
        document = Document.objects.create(
            user=self.other_user,
            title="Private Document",
            file=self.create_test_file(),
            original_filename="private.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.get(
            self.detail_url(
                document.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_rename_other_users_document(
        self,
    ):
        document = Document.objects.create(
            user=self.other_user,
            title="Private Document",
            file=self.create_test_file(),
            original_filename="private.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.patch(
            self.detail_url(
                document.id
            ),
            {
                "title": "Hacked Title",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.title,
            "Private Document",
        )

    def test_cannot_delete_other_users_document(
        self,
    ):
        document = Document.objects.create(
            user=self.other_user,
            title="Private Document",
            file=self.create_test_file(),
            original_filename="private.txt",
            file_type="txt",
            file_size=100,
        )

        response = self.client.delete(
            self.detail_url(
                document.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Document.objects.filter(
                id=document.id
            ).exists()
        )

    def test_anonymous_user_cannot_list_documents(
        self,
    ):
        self.client.logout()

        response = self.client.get(
            self.DOCUMENTS_URL
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    @patch(
        "apps.documents.views.process_document"
    )
    def test_anonymous_user_cannot_upload_document(
        self,
        mock_process_document,
    ):
        self.client.logout()

        test_file = self.create_test_file()

        response = self.client.post(
            self.DOCUMENTS_URL,
            {
                "title": "Unauthorized",
                "file": test_file,
            },
            format="multipart",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

        self.assertFalse(
            Document.objects.filter(
                title="Unauthorized"
            ).exists()
        )

        mock_process_document.assert_not_called()

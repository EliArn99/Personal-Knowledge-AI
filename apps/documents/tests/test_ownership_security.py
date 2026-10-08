import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from apps.documents.models import Document


User = get_user_model()


class DocumentOwnershipSecurityTests(APITestCase):

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
            username="securityuser",
            email="securityuser@example.com",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="othersecurityuser",
            email="othersecurityuser@example.com",
            password="StrongPassword123!",
        )

        self.client.force_login(
            self.user
        )

    def make_file(
        self,
        name="private.txt",
        content=b"Private document content",
    ):
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type="text/plain",
        )

    def create_document(
        self,
        user,
        title="Private Document",
        filename="private.txt",
        content=b"Private document content",
    ):
        uploaded_file = self.make_file(
            name=filename,
            content=content,
        )

        return Document.objects.create(
            user=user,
            title=title,
            file=uploaded_file,
            original_filename=filename,
            file_type="txt",
            file_size=len(content),
        )

    def detail_url(self, document_id):
        return (
            f"/api/documents/{document_id}/"
        )

    def download_url(self, document_id):
        return (
            f"/api/documents/{document_id}/download/"
        )

    def test_user_can_download_own_document(self):
        content = b"My protected document"

        document = self.create_document(
            user=self.user,
            filename="protected.txt",
            content=content,
        )

        response = self.client.get(
            self.download_url(
                document.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        downloaded_content = b"".join(
            response.streaming_content
        )

        self.assertEqual(
            downloaded_content,
            content,
        )

        self.assertIn(
            "attachment",
            response["Content-Disposition"],
        )

        self.assertIn(
            "protected.txt",
            response["Content-Disposition"],
        )

    def test_user_cannot_download_other_users_document(
        self,
    ):
        document = self.create_document(
            user=self.other_user,
            filename="secret.txt",
        )

        response = self.client.get(
            self.download_url(
                document.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_anonymous_user_cannot_download_document(
        self,
    ):
        document = self.create_document(
            user=self.user,
        )

        self.client.logout()

        response = self.client.get(
            self.download_url(
                document.id
            )
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_user_cannot_retrieve_other_users_document(
        self,
    ):
        document = self.create_document(
            user=self.other_user,
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

    def test_document_list_does_not_leak_other_users_documents(
        self,
    ):
        own_document = self.create_document(
            user=self.user,
            title="My Document",
            filename="mine.txt",
        )

        other_document = self.create_document(
            user=self.other_user,
            title="Other Document",
            filename="other.txt",
        )

        response = self.client.get(
            "/api/documents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            item["id"]
            for item in response.data
        }

        self.assertIn(
            own_document.id,
            returned_ids,
        )

        self.assertNotIn(
            other_document.id,
            returned_ids,
        )

    def test_anonymous_user_cannot_use_semantic_search(
        self,
    ):
        self.client.logout()

        response = self.client.post(
            "/api/documents/search/",
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

    def test_anonymous_user_cannot_use_document_ask(
        self,
    ):
        self.client.logout()

        response = self.client.post(
            "/api/documents/ask/",
            {
                "question": "What is Django?"
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

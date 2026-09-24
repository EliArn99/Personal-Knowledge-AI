from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def document_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()

    unique_filename = (
        f"{uuid4().hex}{extension}"
    )

    return (
        f"documents/"
        f"user_{instance.user_id}/"
        f"{unique_filename}"
    )


class Document(models.Model):

    class ExtractionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField(
        max_length=255,
    )

    file = models.FileField(
        upload_to=document_upload_path,
    )

    original_filename = models.CharField(
        max_length=255,
    )

    file_type = models.CharField(
        max_length=20,
    )

    file_size = models.PositiveBigIntegerField()

    # Extracted document content

    extracted_text = models.TextField(
        blank=True,
        default="",
    )

    extraction_status = models.CharField(
        max_length=20,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING,
    )

    extraction_error = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title



class DocumentChunk(models.Model):

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )

    chunk_index = models.PositiveIntegerField()

    content = models.TextField()

    embedding = models.JSONField(
        null=True,
        blank=True,
    )

    embedding_model = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "chunk_index",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "document",
                    "chunk_index",
                ],
                name="unique_document_chunk_index",
            ),
        ]

    def __str__(self):
        return (
            f"{self.document.title} "
            f"- Chunk {self.chunk_index}"
        )

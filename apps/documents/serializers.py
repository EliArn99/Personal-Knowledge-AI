from pathlib import Path

from django.urls import reverse

from rest_framework import serializers

from .models import Document


MAX_FILE_SIZE = (
    10 * 1024 * 1024
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}


class DocumentSerializer(
    serializers.ModelSerializer
):

    download_url = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Document

        fields = (
            "id",
            "title",
            "file",
            "download_url",
            "original_filename",
            "file_type",
            "file_size",
            "extraction_status",
            "extraction_error",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "download_url",
            "original_filename",
            "file_type",
            "file_size",
            "extraction_status",
            "extraction_error",
            "created_at",
            "updated_at",
        )

        extra_kwargs = {
            "file": {
                "write_only": True,
            },

            "title": {
                "required": False,
                "allow_blank": True,
            },
        }

    def get_download_url(self, obj):
        return reverse(
            "document-download",
            kwargs={
                "pk": obj.pk,
            },
        )

    def validate_file(self, file):
        extension = (
            Path(file.name)
            .suffix
            .lower()
        )

        if (
            extension
            not in ALLOWED_EXTENSIONS
        ):
            raise serializers.ValidationError(
                "Unsupported file type. "
                "Allowed file types: "
                "PDF, TXT, MD."
            )

        if file.size == 0:
            raise serializers.ValidationError(
                "Cannot upload an empty file."
            )

        if file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File is too large. "
                "Maximum file size is 10 MB."
            )

        return file

    def validate_title(self, value):
        title = value.strip()

        if (
            self.instance is not None
            and not title
        ):
            raise serializers.ValidationError(
                "Document title cannot be empty."
            )

        return title

    def validate(self, attrs):
        if (
            self.instance is not None
            and "file" in attrs
        ):
            raise serializers.ValidationError(
                {
                    "file":
                        "Replacing an existing "
                        "document file is not "
                        "supported."
                }
            )

        return attrs

    def create(self, validated_data):
        file = validated_data["file"]

        original_filename = (
            Path(file.name)
            .name[:255]
        )

        extension = (
            Path(original_filename)
            .suffix
            .lower()
        )

        title = (
            validated_data
            .get(
                "title",
                "",
            )
            .strip()
        )

        if not title:
            title = (
                Path(original_filename)
                .stem[:255]
            )

        validated_data["title"] = (
            title
        )

        validated_data[
            "original_filename"
        ] = original_filename

        validated_data[
            "file_type"
        ] = extension.lstrip(".")

        validated_data[
            "file_size"
        ] = file.size

        return super().create(
            validated_data
        )


class DocumentDetailSerializer(
    DocumentSerializer
):

    class Meta(DocumentSerializer.Meta):

        fields = (
            DocumentSerializer.Meta.fields
            + ("extracted_text",)
        )

        read_only_fields = (
            DocumentSerializer.Meta.read_only_fields
            + ("extracted_text",)
        )

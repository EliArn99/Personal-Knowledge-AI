from pathlib import Path

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
    class Meta:
        model = Document

        fields = (
            "id",
            "title",
            "file",
            "original_filename",
            "file_type",
            "file_size",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "original_filename",
            "file_type",
            "file_size",
            "created_at",
            "updated_at",
        )

        extra_kwargs = {
            "title": {
                "required": False,
                "allow_blank": True,
            },
        }


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

        if file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File is too large. "
                "Maximum file size is 10 MB."
            )

        return file


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
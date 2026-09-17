from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(
    admin.ModelAdmin
):
    list_display = (
        "id",
        "title",
        "user",
        "file_type",
        "file_size",
        "created_at",
    )

    list_filter = (
        "file_type",
        "created_at",
    )

    search_fields = (
        "title",
        "original_filename",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "original_filename",
        "file_type",
        "file_size",
        "created_at",
        "updated_at",
    )

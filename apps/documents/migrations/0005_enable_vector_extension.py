from django.db import migrations

from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0004_document_indexing_error_document_indexing_status"),
    ]

    operations = [
        VectorExtension(),
    ]
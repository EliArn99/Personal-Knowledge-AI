from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

from apps.documents.models import DocumentChunk


EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class Command(BaseCommand):
    help = "Regenerate embeddings for all document chunks."

    def handle(self, *args, **options):
        self.stdout.write(
            "Loading embedding model..."
        )

        model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        chunks = list(
            DocumentChunk.objects.all()
        )

        total = len(chunks)

        if total == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No document chunks found."
                )
            )
            return

        self.stdout.write(
            f"Found {total} chunks."
        )

        texts = [
            chunk.content
            for chunk in chunks
        ]

        self.stdout.write(
            "Generating embeddings..."
        )

        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
        )

        self.stdout.write(
            "Saving embeddings..."
        )

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            chunk.embedding = embedding.tolist()
            chunk.embedding_model = EMBEDDING_MODEL

        DocumentChunk.objects.bulk_update(
            chunks,
            [
                "embedding",
                "embedding_model",
            ],
            batch_size=100,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully re-indexed "
                f"{total} document chunks."
            )
        )

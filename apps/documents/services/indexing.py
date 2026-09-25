from django.db import transaction

from apps.documents.models import (
    DocumentChunk,
)

from .chunking import (
    split_text_into_chunks,
)

from .embeddings import (
    EMBEDDING_MODEL_NAME,
    generate_embeddings,
)


class DocumentIndexingError(Exception):
    pass


def index_document(document):

    if document.extraction_status != "ready":
        raise DocumentIndexingError(
            "The document text is not ready."
        )

    texts = split_text_into_chunks(
        document.extracted_text
    )

    if not texts:
        raise DocumentIndexingError(
            "The document has no text to index."
        )

    # Generate embeddings before changing
    # existing database records.

    vectors = generate_embeddings(
        texts
    )

    if len(texts) != len(vectors):
        raise DocumentIndexingError(
            "Embedding count does not "
            "match chunk count."
        )

    chunks = []

    for index, (text, vector) in enumerate(
        zip(texts, vectors)
    ):

        chunks.append(
            DocumentChunk(
                document=document,
                chunk_index=index,
                content=text,
                embedding=vector,
                embedding_model=(
                    EMBEDDING_MODEL_NAME
                ),
            )
        )

    # Replace old chunks atomically.
    # Running indexing twice will not
    # duplicate the document chunks.

    with transaction.atomic():

        document.chunks.all().delete()

        DocumentChunk.objects.bulk_create(
            chunks,
            batch_size=100,
        )

    return len(chunks)

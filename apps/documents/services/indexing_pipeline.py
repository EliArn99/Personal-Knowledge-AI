import logging

from .indexing import index_document


logger = logging.getLogger(__name__)


def process_document_indexing(document):
    """
    Creates chunks and embeddings for a document
    whose text extraction has succeeded.
    """

    if document.extraction_status != "ready":
        return False


    document.indexing_status = "pending"
    document.indexing_error = ""

    document.save(
        update_fields=[
            "indexing_status",
            "indexing_error",
            "updated_at",
        ]
    )

    try:



        index_document(document)

    except Exception:

        logger.exception(
            "Document indexing failed "
            "for document ID %s",
            document.pk,
        )

        document.indexing_status = "failed"

        document.indexing_error = (
            "Could not generate document "
            "embeddings. Check the server logs."
        )

        document.save(
            update_fields=[
                "indexing_status",
                "indexing_error",
                "updated_at",
            ]
        )

        return False


    document.indexing_status = "ready"
    document.indexing_error = ""

    document.save(
        update_fields=[
            "indexing_status",
            "indexing_error",
            "updated_at",
        ]
    )

    return True

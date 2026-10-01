from apps.documents.services.search import (
    semantic_search,
)

from .ai_service import (
    AIServiceError,
    generate_chat_response,
)


class RAGServiceError(Exception):
    """Raised when RAG answer generation fails."""
    pass


def build_context(
        search_results,
):
    context_parts = []

    for index, result in enumerate(
            search_results,
            start=1,
    ):
        chunk = result["chunk"]

        context_parts.append(
            (
                f"[Source {index}]\n"
                f"Document: "
                f"{chunk.document.title}\n"
                f"Chunk: "
                f"{chunk.chunk_index}\n"
                f"Similarity: "
                f"{result['score']:.4f}\n\n"
                f"{chunk.content}"
            )
        )

    return "\n\n---\n\n".join(
        context_parts
    )


def build_sources(
        search_results,
):
    sources = []

    for result in search_results:
        chunk = result["chunk"]

        sources.append(
            {
                "document_id":
                    chunk.document_id,

                "document_title":
                    chunk.document.title,

                "chunk_index":
                    chunk.chunk_index,

                "score":
                    round(
                        result["score"],
                        6,
                    ),
            }
        )

    return sources


def answer_with_documents(
        user,
        question,
        limit=5,
        min_score=0.30,
):
    question = question.strip()

    if not question:
        raise RAGServiceError(
            "Question cannot be empty."
        )

    search_results = semantic_search(
        user=user,
        query=question,
        limit=limit,
        min_score=min_score,
    )

    if not search_results:
        return {
            "answer": (
                "I could not find enough "
                "relevant information in "
                "your documents to answer "
                "this question."
            ),
            "sources": [],
        }

    context = build_context(
        search_results
    )

    messages = [
        {
            "role": "user",
            "content": (
                "Answer the user's question "
                "using only the document "
                "context below.\n\n"

                "If the context does not "
                "contain enough information, "
                "say that the documents do "
                "not provide enough "
                "information.\n\n"

                "Do not invent facts that "
                "are not supported by the "
                "document context.\n\n"

                "Do not add citations, source names, "
                "chunk numbers, or reference markers "
                "to the answer. Sources are displayed "
                "separately by the application.\n\n"

                "DOCUMENT CONTEXT:\n\n"
                f"{context}\n\n"

                "USER QUESTION:\n\n"
                f"{question}"
            ),
        }
    ]

    try:
        answer = generate_chat_response(
            messages
        )

    except AIServiceError as exc:
        raise RAGServiceError(
            "Failed to generate a "
            "document-based AI answer."
        ) from exc

    return {
        "answer": answer,
        "sources": build_sources(
            search_results
        ),
    }

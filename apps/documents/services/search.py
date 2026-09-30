import math

from apps.documents.models import DocumentChunk

from .embeddings import generate_embeddings


def dot_product(vector_a, vector_b):
    return sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )


def vector_norm(vector):
    return math.sqrt(
        sum(
            value * value
            for value in vector
        )
    )


def cosine_similarity(
    vector_a,
    vector_b,
):
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    denominator = (
        vector_norm(vector_a)
        * vector_norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    return (
        dot_product(
            vector_a,
            vector_b,
        )
        / denominator
    )


def semantic_search(
    user,
    query,
    limit=5,
    min_score=0.30,
):
    query = query.strip()

    if not query:
        return []

    query_vectors = generate_embeddings(
        [query]
    )

    query_embedding = query_vectors[0]

    chunks = (
        DocumentChunk.objects
        .filter(
            document__user=user,
            embedding__isnull=False,
        )
        .select_related(
            "document"
        )
    )

    results = []

    for chunk in chunks:

        similarity = cosine_similarity(
            query_embedding,
            chunk.embedding,
        )
        if similarity < min_score:
            continue

        results.append(
            {
                "chunk": chunk,
                "score": similarity,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:limit]

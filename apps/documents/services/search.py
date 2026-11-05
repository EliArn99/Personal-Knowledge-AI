from pgvector.django import CosineDistance

from apps.documents.models import DocumentChunk

from .embeddings import generate_embeddings


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
        .annotate(
            distance=CosineDistance(
                "embedding",
                query_embedding,
            )
        )
        .order_by(
            "distance"
        )
    )

    results = []

    for chunk in chunks:
        similarity = 1.0 - float(
            chunk.distance
        )

        if similarity < min_score:
            continue

        results.append(
            {
                "chunk": chunk,
                "score": similarity,
            }
        )

        if len(results) >= limit:
            break

    return results

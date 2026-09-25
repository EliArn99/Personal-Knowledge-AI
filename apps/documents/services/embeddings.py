from functools import lru_cache

from sentence_transformers import (
    SentenceTransformer,
)


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@lru_cache(maxsize=1)
def get_embedding_model():

    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )


def generate_embeddings(
    texts,
):

    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return vectors.tolist()
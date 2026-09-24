CHUNK_SIZE = 400
CHUNK_OVERLAP = 60


def split_text_into_chunks(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):
    if not 0 <= overlap < chunk_size:
        raise ValueError(
            "Overlap must be smaller "
            "than chunk size."
        )

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text),
        )

        # Prefer splitting at whitespace.

        if end < len(text):

            last_space = text.rfind(
                " ",
                start,
                end,
            )

            if last_space > start:
                end = last_space + 1

        chunk = text[
            start:end
        ].strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= len(text):
            break

        # Keep part of the previous
        # chunk as context.

        start = max(
            start + 1,
            end - overlap,
        )

    return chunks

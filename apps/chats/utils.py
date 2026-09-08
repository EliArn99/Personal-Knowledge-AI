def generate_chat_title(content, max_length=50):
    """
    Generate a short chat title from the first user message.
    """

    content = " ".join(content.strip().split())

    if not content:
        return "New Chat"

    if len(content) <= max_length:
        return content

    shortened = content[:max_length]

    # Avoid cutting a word in half.
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]

    shortened = shortened.rstrip(".,!?;:")

    return f"{shortened}..."
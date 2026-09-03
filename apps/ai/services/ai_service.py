from django.conf import settings
from openai import OpenAI, OpenAIError


class AIServiceError(Exception):
    """Raised when the AI provider cannot generate a response."""
    pass


def get_ai_client():
    if not settings.GROQ_API_KEY:
        raise AIServiceError(
            "GROQ_API_KEY is not configured."
        )

    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )


def generate_chat_response(messages):
    client = get_ai_client()

    try:
        response = client.responses.create(
            model=settings.AI_MODEL,
            instructions=(
                "You are Personal Knowledge AI. "
                "Be helpful, accurate, and concise. "
                "Reply in the same language as the user "
                "unless the user asks otherwise."
            ),
            input=messages,
        )

    except OpenAIError as exc:
        raise AIServiceError(
            "Failed to generate AI response."
        ) from exc

    answer = response.output_text

    if not answer:
        raise AIServiceError(
            "The AI returned an empty response."
        )

    return answer.strip()
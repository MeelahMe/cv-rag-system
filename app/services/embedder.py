import os

from google import genai

# embedding-001 was shut down by Google in October 2025. This is the
# current replacement model, used via the current google-genai SDK
# (the old google.generativeai package is fully deprecated).
EMBEDDING_MODEL = "gemini-embedding-001"

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generate_embedding(text: str):
    """Generate an embedding for the given text using Google's Gemini API."""
    try:
        client = _get_client()
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        return result.embeddings[0].values
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")

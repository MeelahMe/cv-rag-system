import os
import google.generativeai as genai

# Define your embedding model
EMBEDDING_MODEL = "models/embedding-001"

def generate_embedding(text: str):
    """Generate an embedding for the given text using Google's Generative AI."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")

    # Configure the API key
    genai.configure(api_key=api_key)

    try:
        # Correct payload for your library version
        response = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,  # <- Corrected here
            task_type="retrieval_document"
        )
        return response["embedding"]
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}")

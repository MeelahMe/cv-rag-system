# app/services/scorer.py

import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_URL = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedText"

HEADERS = {
    "Content-Type": "application/json"
}

def embed(text):
    """
    Generate an embedding for the provided text using Gemini Embedding API.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    payload = {
        "model": "models/embedding-001",
        "content": text
    }

    response = requests.post(
        f"{GEMINI_EMBEDDING_URL}?key={GEMINI_API_KEY}",
        headers=HEADERS,
        json=payload
    )

    if response.status_code != 200:
        raise RuntimeError(f"Failed to embed text: {response.status_code} - {response.text}")

    return response.json()["embedding"]["values"]

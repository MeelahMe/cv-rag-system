import math

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.auth import verify_api_key
from app.services.embedder import generate_embedding

router = APIRouter()


class ScoreRequest(BaseModel):
    query: str
    text: str


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Proper cosine similarity, bounded to [-1, 1]. The previous
    implementation was a raw, unnormalized dot product, which is
    sensitive to vector magnitude, not just directional alignment -
    not a valid similarity metric on its own.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@router.post("/score")
async def score_text(request: ScoreRequest, api_key: str = Depends(verify_api_key)):
    """
    Generate embeddings for both query and text, then return a proper
    cosine similarity score, consistent with the scoring used in
    app/services/searcher.py's search results.
    """
    try:
        query_embedding = generate_embedding(request.query)
        text_embedding = generate_embedding(request.text)

        similarity = round(cosine_similarity(query_embedding, text_embedding), 4)

        return {"similarity_score": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed text: {e}")


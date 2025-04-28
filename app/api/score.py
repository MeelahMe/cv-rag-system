from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedder import generate_embedding

router = APIRouter()

class ScoreRequest(BaseModel):
    query: str
    text: str

@router.post("/score")
async def score_text(request: ScoreRequest):
    """
    Generate embeddings for both query and text, then return a nicely rounded similarity score.
    """
    try:
        query_embedding = generate_embedding(request.query)
        text_embedding = generate_embedding(request.text)

        # Simple similarity calculation
        similarity = sum(q * t for q, t in zip(query_embedding, text_embedding))

        # Round the result to 4 decimal places
        similarity = round(similarity, 4)

        return {"Similarity score": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed text: {e}")


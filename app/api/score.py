from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.auth import verify_api_key
from app.services.embedder import generate_embedding
from app.services.text_quality import cosine_similarity, is_likely_stuffed

router = APIRouter()


class ScoreRequest(BaseModel):
    query: str
    text: str


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
        flagged = is_likely_stuffed(request.text)

        # Penalize scores for text that looks keyword-stuffed rather
        # than genuinely written. This is a partial mitigation, not a
        # complete fix - it only catches literal word repetition, not
        # e.g. a CV stuffed with many unique but unrelated buzzwords.
        if flagged:
            similarity = round(similarity * 0.5, 4)

        return {"similarity_score": similarity, "flagged_low_diversity": flagged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed text: {e}")

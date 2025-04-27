# app/api/score.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import scorer, searcher

router = APIRouter()

class ScoreRequest(BaseModel):
    text: str

@router.post("/score")
def score_cv(request: ScoreRequest):
    """
    Embed the CV text and perform a similarity search against indexed CVs.
    """
    try:
        embedding = scorer.embed(request.text)
        results = searcher.search_cvs(query_embedding=embedding)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

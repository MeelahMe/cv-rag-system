from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.embedder import generate_embedding
from app.services.searcher import search_cvs

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    language: Optional[str] = None
    min_years_experience: Optional[int] = None
    skills: Optional[List[str]] = None
    job_title: Optional[str] = None

@router.post("/search")
async def search(request: SearchRequest):
    """
    Accept a natural language query, convert it to an embedding,
    and return top-matching CVs from the vector database with optional filters.
    """
    try:
        # Step 1: Embed the query
       embedding = generate_embedding(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e}")

    # Step 2: Build filters if provided
    filters = {}
    if request.language:
        filters["language"] = request.language
    if request.min_years_experience is not None:
        filters["min_years_experience"] = request.min_years_experience
    if request.skills:
        filters["skills"] = request.skills
    if request.job_title:
        filters["job_title"] = request.job_title

    try:
        # Step 3: Search Weaviate
        results = search_cvs(embedding, top_k=request.top_k, filters=filters)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search CVs: {e}")

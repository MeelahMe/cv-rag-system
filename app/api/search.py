from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedder import generate_embedding
from app.services.searcher import search_cvs

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search")
async def search(request: SearchRequest):
    """
    Accept a natural language query, convert it to an embedding,
    and return top-matching CVs from the vector database.
    """
    try:
        embedding = generate_embedding(request.query)
        results = search_cvs(embedding, top_k=request.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


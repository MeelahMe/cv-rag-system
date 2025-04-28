from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.embedder import generate_embedding
from app.services.searcher import insert_cv, insert_cvs_bulk
from fastapi import Depends
from app.services.auth import verify_api_key


router = APIRouter()

class InsertCVRequest(BaseModel):
    text: str = Field(..., description="Full parsed CV text")
    language: str = Field(..., description="Language of the CV")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    job_title: str = Field(..., description="Primary job title")
    years_experience: Optional[int] = Field(default=0, description="Years of experience")

class BulkInsertCVRequest(BaseModel):
    cvs: List[InsertCVRequest]

@router.post("/insert-cv")
async def insert_cv_endpoint(request: InsertCVRequest, api_key: str = Depends(verify_api_key)):
    """
    Insert a new CV into the vector database with its metadata and embedding.
    """
    try:
        embedding = generate_embedding(request.text)
        metadata = {
            "language": request.language,
            "skills": request.skills,
            "job_title": request.job_title,
            "years_experience": request.years_experience
        }
        insert_cv(request.text, embedding, metadata)
        return {"message": "CV inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-insert-cv")
async def bulk_insert_cvs(request: BulkInsertCVRequest, api_key: str = Depends(verify_api_key)):
    """
    Bulk insert multiple CVs into the vector database.
    """
    try:
        insert_cvs_bulk(request.cvs)
        return {"message": f"{len(request.cvs)} CVs inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# app/api/parse.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import parse_pdf_with_gemini
from app.services.embedder import generate_embedding

router = APIRouter()

@router.post("/parse")
async def parse_cv(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        file_bytes = await file.read()
        structured_text = parse_pdf_with_gemini(file_bytes)
        embedding = generate_embedding(structured_text)

        return {
            "text": structured_text,
            "embedding": embedding
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


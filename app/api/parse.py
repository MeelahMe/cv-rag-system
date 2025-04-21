from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import parse_pdf_with_gemini
from app.services.embedder import generate_embedding
from app.services.searcher import insert_cv

router = APIRouter()

@router.post("/parse")
async def parse_cv(file: UploadFile = File(...)):
    """
    Parses a PDF CV, generates an embedding, adds metadata,
    and inserts the result into the vector database.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Read PDF file bytes
        file_bytes = await file.read()

        # Step 1: Extract structured text (stubbed Gemini parser)
        structured_text = parse_pdf_with_gemini(file_bytes)

        # Step 2: Generate semantic embedding (stubbed Gemini embedder)
        embedding = generate_embedding(structured_text)

        # Step 3: Define metadata (for now, hardcoded)
        metadata = {
            "language": "English",
            "skills": ["Python", "APIs"],
            "job_title": "Software Engineer",
            "years_experience": 3
        }

        # Step 4: Insert CV into Weaviate
        insert_cv(structured_text, embedding, metadata)

        # Return result
        return {
            "message": "CV parsed and stored successfully.",
            "text": structured_text,
            "embedding_preview": embedding[:5]  # show only first 5 values
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

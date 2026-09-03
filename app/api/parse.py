from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.services import embedder, parser, searcher
from app.services.auth import verify_api_key

router = APIRouter()


@router.post("/parse")
async def parse_cv(
    file: UploadFile = File(...), api_key: str = Depends(verify_api_key)
):
    """
    Parse a CV file, embed it, extract metadata, and store it.
    Mirrors the error-handling pattern used in insert.py, search.py,
    and score.py - a clean {"detail": ...} JSON response instead of an
    unhandled exception, distinguishing a bad input (400) from an
    internal failure (500).
    """
    try:
        content = await file.read()
        text = parser.parse_content(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        embedding = embedder.generate_embedding(text)
        metadata = parser.extract_metadata(text)
        searcher.insert_cv(text, embedding, metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "CV parsed and stored successfully", "metadata": metadata}

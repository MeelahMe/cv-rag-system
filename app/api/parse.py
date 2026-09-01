from fastapi import APIRouter, Depends, File, UploadFile

from app.services import embedder, parser, searcher
from app.services.auth import verify_api_key

router = APIRouter()


@router.post("/parse")
async def parse_cv(file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    content = await file.read()
    text = parser.parse_content(content, file.filename)
    embedding = embedder.generate_embedding(text)

    metadata = parser.extract_metadata(text)
    searcher.insert_cv(text, embedding, metadata)

    return {"message": "CV parsed and stored successfully", "metadata": metadata}

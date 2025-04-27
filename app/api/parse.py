from fastapi import APIRouter, UploadFile, File
from app.services import parser, embedder, searcher

router = APIRouter()

@router.post("/parse")
async def parse_cv(file: UploadFile = File(...)):
    content = await file.read()
    text = parser.parse_content(content, file.filename)
    embedding = embedder.generate_embedding(text)

    metadata = parser.extract_metadata(text)
    searcher.insert_cv(text, embedding, metadata)

    return {"message": "CV parsed and stored successfully", "metadata": metadata}

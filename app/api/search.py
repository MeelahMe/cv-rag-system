# app/api/search.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/search")
async def search_cvs():
    return {"message": "Search endpoint coming soon"}


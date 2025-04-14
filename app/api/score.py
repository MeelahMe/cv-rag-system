# app/api/score.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/score")
async def score_cv():
    return {"message": "Score endpoint coming soon"}


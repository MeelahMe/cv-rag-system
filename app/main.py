from fastapi import FastAPI
from app.api import parse, search, score

app = FastAPI(title="Gemini CV RAG System")

app.include_router(parse.router)
app.include_router(search.router)
app.include_router(score.router)


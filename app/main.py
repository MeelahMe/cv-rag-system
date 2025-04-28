from fastapi import FastAPI
from app.api import parse, search, score, insert
from app.services.searcher import init_schema

def create_app() -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    async def startup_event():
        """
        Run any startup tasks here, like initializing the Weaviate schema.
        """
        init_schema()

    # Register routers
    app.include_router(parse.router, prefix="/parse", tags=["Parsing"])
    app.include_router(search.router, prefix="/search", tags=["Search"])
    app.include_router(score.router, prefix="/score", tags=["Scoring"])
    app.include_router(insert.router, tags=["Insert"])

    return app

app = create_app()

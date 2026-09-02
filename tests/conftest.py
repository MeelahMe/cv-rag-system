import os

import pytest
from fastapi.testclient import TestClient

# Set env vars before app.main is imported, so verify_api_key and
# get_client() have real values to work with. TEST_API_KEY is what
# tests send back in the X-API-Key header.
os.environ.setdefault("API_KEY", "test-api-key")
os.environ.setdefault("GEMINI_API_KEY", "test-placeholder-not-a-real-key")
os.environ.setdefault("VECTOR_DB_HOST", "http://localhost:8080")

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    # Deliberately NOT using "with TestClient(app) as client" - that
    # would trigger the startup event, which calls init_schema() and
    # tries to make a real Weaviate connection. Plain TestClient(app)
    # skips lifespan entirely, which is what we want for these tests:
    # every route's real dependency (embedder, searcher) gets mocked
    # at the test level instead.
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": os.environ["API_KEY"]}

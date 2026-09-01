# Gemini-Powered CV Retrieval System

A multilingual, vector-based retrieval system for semantically searching CVs using Google's Gemini API. It combines FastAPI, Docker, and Weaviate to parse, embed, store, and score CV documents.

The system is modular and containerized, and it's meant to run locally or in the cloud.

## Current status

The core parse, insert, search, and score flow works, is authenticated, and has been verified end to end against the real Gemini and Weaviate stack. There is no automated test suite yet: the only testing right now is the manual shell scripts described below. Adding real pytest coverage is next on the list. See [Roadmap](#roadmap).

## System design overview

For architecture diagrams, data flow, scalability considerations, and future improvements, see the [system design document](./docs/system_design_overview.md).

## API documentation

You can test the full API using the included Postman collection:

- [Download the CV RAG System API Postman collection](./CV%20RAG%20System%20API.postman_collection.json)

Use the `cv-rag-system-local` Postman environment, and set your own `base_url` and `api_key` variables.

---

## Features

- Parse and embed CVs in English, Arabic, and Spanish using the Gemini API
- Store embeddings with metadata in a Weaviate vector database
- Perform semantic search with optional metadata filtering
- Score a query against a CV using proper cosine similarity
- API key authentication required on every endpoint
- Modular architecture with clear separation between API routes and services
- Local development with Docker Compose
- Seed the database with realistic fake CVs for testing and demos

---

## Project structure

```bash
cv-rag-system/
├── app/
│   ├── api/                   # API route definitions
│   │   ├── insert.py
│   │   ├── parse.py
│   │   ├── score.py
│   │   └── search.py
│   ├── services/              # Core service logic
│   │   ├── auth.py            # API key verification
│   │   ├── embedder.py
│   │   ├── parser.py
│   │   └── searcher.py
│   ├── scripts/               # Development scripts (e.g. seeding)
│   │   └── seed.py
│   └── main.py                # FastAPI application setup
├── docs/
│   └── system_design_overview.md
├── bulk_insert.sh             # Bulk insert sample CVs
├── test_features.sh           # End-to-end manual test script
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.template               # Environment variable template
```

---

## Setup instructions

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)

### 1. Clone the repository

```bash
git clone https://github.com/MeelahMe/cv-rag-system.git
cd cv-rag-system
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the template file and fill in your own values:

```bash
cp .env.template .env
```

You'll need a real Gemini API key and a value for `API_KEY`. `API_KEY` isn't a Google key. It's a secret you make up yourself, and every request to this API needs to send it back in an `X-API-Key` header.

---

## Running the application

To run locally:

```bash
uvicorn app.main:app --reload
```

To run fully containerized (FastAPI and Weaviate together):

```bash
docker-compose up --build
```

Once it's running, visit `http://localhost:8000/docs` for the interactive API documentation.

---

## Available API endpoints

All endpoints require an `X-API-Key` header matching your configured `API_KEY`.

| Method | Endpoint | Description |
|:------|:---------|:------------|
| POST | `/insert-cv` | Insert a single parsed CV |
| POST | `/bulk-insert-cv` | Insert multiple CVs at once |
| POST | `/parse/parse` | Parse a CV file and embed it |
| POST | `/search/search` | Semantic search against stored CVs |
| POST | `/score/score` | Score a query against a CV using cosine similarity |

---

## Seeding the database with fake CVs

This project includes a Faker-powered seeding script that generates realistic CV data for testing and demos.

Make sure your API server is running, then:

```bash
python app/scripts/seed.py
```

The script inserts multiple realistic CVs into the database through the API. You can change how many get seeded by editing `num_cvs` in `seed.py`.

## Local development workflow

### Full local testing

1. Start the API and vector database:

```bash
docker-compose down -v
docker-compose up --build
```

2. In a second terminal, run the end-to-end test script:

```bash
./test_features.sh
```

3. Seed sample data:

```bash
./bulk_insert.sh
python app/scripts/seed.py
```

4. Explore the API through Postman or your browser at `http://localhost:8000/docs`.

---

## Troubleshooting

### Error: `Form data requires "python-multipart" to be installed`

```bash
pip install python-multipart
```

### Error: `Connection Refused`

Make sure the FastAPI server is running and reachable at `http://localhost:8000`.

### Error: `Invalid or missing API key`

Every endpoint requires the `X-API-Key` header now, not just the insert routes. Check that it's set and matches your `API_KEY` value in `.env`.

---

## Roadmap

- [x] Auth enforced on every endpoint, not just insert
- [x] Fixed `/score`'s similarity calculation (was a raw, unnormalized dot product, now proper cosine similarity)
- [x] Removed dead code (`scorer.py`, an unused parallel embedding implementation, and an empty `utils/helpers.py`)
- [x] Migrated off the deprecated `google.generativeai` SDK and the shut-down `embedding-001` model to the current `google-genai` SDK and `gemini-embedding-001`
- [x] Fixed `searcher.py`'s Weaviate connection so it no longer blocks at import time
- [x] Pinned `requirements.txt` to actual working versions, removed the unused `openai` dependency
- [x] Fixed `.gitignore` silently excluding `.env.template`, and fixed `test_features.sh` calling a URL that never existed
- [ ] Real pytest coverage. `tests/` currently exists but is empty; the only testing today is the manual shell scripts above
- [ ] CI pipeline: tests, gitleaks, Semgrep, Bandit, Trivy, same setup used on the other projects in this portfolio
- [ ] Test the RAG pipeline for prompt injection and retrieval or scoring poisoning through CV content, and document the findings
- [ ] Bulk ingestion optimization (async batch inserts)
- [ ] Frontend interface for CV search and scoring
- [ ] Enhanced scoring explanation (natural language output)
- [ ] Public deployment on GCP Cloud Run

---

## Author

Jameelah Mercer
[LinkedIn](https://www.linkedin.com/in/jameelahmercer)

# Gemini-Powered CV Retrieval System

A multilingual, vector-based retrieval system for semantically searching CVs using Google's Gemini API. This project combines FastAPI, Docker, and Weaviate to create a scalable backend for parsing, embedding, storing, and scoring CV documents.

The system is modular, containerized, and designed for local or cloud deployment.

##  System Design Overview

For a detailed system design of the Multilingual CV RAG system, including architecture diagrams, data flow, scalability considerations, and future improvements, see the [System Design Document](./docs/system_design_overview.md).

---

## Features

- Parse and embed CVs in English, Arabic, and Spanish using the Gemini API
- Store embeddings with metadata in a Weaviate vector database
- Perform semantic search with optional metadata filtering
- Score job descriptions against CVs to assess relevance
- Modular architecture with clear separation of API routes, services, and utilities
- Local development using Docker Compose

---

## Project Structure

```bash
cv-rag-system/
├── app/
│   ├── api/                   # API route definitions
│   │   ├── insert.py
│   │   ├── parse.py
│   │   ├── score.py
│   │   └── search.py
│   ├── services/              # Core service logic
│   │   ├── embedder.py
│   │   ├── parser.py
│   │   ├── scorer.py
│   │   └── searcher.py
│   └── main.py                # FastAPI application setup
├── bulk_insert.sh             # Bulk insert sample CVs
├── test_features.sh           # End-to-end testing script
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.template              # Environment variable template
```

---

## Setup instructions

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cv-rag-system.git
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

Copy the template file and update it with your configuration:

```bash
cp .env.template .env
```

Set values such as your Gemini API key and vector database host.

---

## Running the application

To run locally, start the development server:

```bash
uvicorn app.main:app --reload
```

To runfully conntainerized (FastAPI + Weaviate):

```bash
docker-compose up --build
```

Once the server is running, visit \`http://localhost:8000/docs\` to access the interactive API documentation.

---

## Available API Endpoints

| Method | Endpoint | Description |
|:------|:---------|:------------|
| POST | `/insert-cv` | **[Insert]** Insert a single parsed CV |
| POST | `/bulk-insert-cv` | **[Insert]** Insert multiple CVs at once |
| POST | `/parse/parse` | **[Parse]** Parse and embed a CV text input |
| POST | `/search/search` | **[Search]** Perform semantic search against stored CVs |
| POST | `/score/score` | **[Score]** Score a job description against a stored CV |


---

## Testing the system

 Start the application run:

```bash
docker-compose down -v
docker-compose up --build
```

In a second terminal run end-to-end tests:

```bash
./test_features.sh
```

```bash
./bulk_insert.sh
```

---

## Troubleshooting

### Error: `Form data requires "python-multipart" to be installed`

Install the required package:

```bash
pip install python-multipart
```

### Error: `module 'app.api.search' has no attribute 'router'`

Ensure that `search.py` contains the following:

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/search")
async def search():
    return {"message": "Coming soon"}
```

---

## Future Improvements

- Seed database with synthetic CVs using Faker
- API key authentication for protected endpoints
- Bulk ingestion optimization (async batch inserts)
- Postman Collection export for easier testing and API documentation
- Optional frontend interface for CV search and scoring
- Enhanced scoring explanation (natural language output)

---

## Author

Jameelah Mercer  
[LinkedIn](https://www.linkedin.com/in/jameelahmercer)


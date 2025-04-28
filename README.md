# Gemini-Powered CV Retrieval System

A multilingual, vector-based retrieval system for semantically searching CVs using Google's Gemini API.  
This project combines FastAPI, Docker, and Weaviate to create a scalable backend for parsing, embedding, storing, and scoring CV documents.

The system is modular, containerized, and designed for local or cloud deployment.

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
| POST | `/insert-cv` | Insert a single parsed CV |
| POST | `/bulk-insert-cv` | Insert multiple CVs at once |
| POST | `/parse/parse` | Parse and embed a CV text input |
| POST | `/search/search` | Semantic search against stored CVs |
| POST | `/score/score` | Score a job description against a CV |

---

## Testing the `/parse` endpoint

1. Start the application:
   
   ```bash
   uvicorn app.main:app --reload
   ```

2. Navigate to:
   `http://localhost:8000/docs`
3. Select the `POST /parse` endpoint.
4. Upload a PDF file.
5. Submit the request. The response includes the extracted text and a 768-dimensional vector.

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

### Error: `There is no tracking information for the current branch`

Set your local branch to track the remote:

```bash
git branch --set-upstream-to=origin/main main
```

### Error: `Updates were rejected because the tip of your current branch is behind`

Use rebase to integrate changes safely:

```bash
git pull origin main --rebase
git push origin main
```

Alternatively, use force push to overwrite the remote:

```bash
git push origin main --force
```

---

## Upcoming features

- Gemini API integration for production
- Embedding storage using Weaviate or Qdrant
- Scoring logic and explanation framework
- Batch processing for large datasets
- GCP deployment and public demo endpoint

---

## Author

Jameelah Mercer  
[LinkedIn](https://www.linkedin.com/in/jameelahmercer)
EOF


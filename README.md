# Gemini-Powered CV RAG System

This repository contains a multilingual Retrieval-Augmented Generation (RAG) system for processing, embedding, and semantically searching CVs in PDF format. It uses the Google Gemini API to extract structured text and generate semantic embeddings, and a vector database to enable fast, metadata-aware search.

The system is modular, containerized, and designed for local use or deployment on Google Cloud Platform (GCP).

---

## Features

- Parse CV PDFs in Arabic and English using the Gemini API.
- Generate 768-dimensional semantic embeddings.
- Store and query embeddings using a vector database.
- Expose three REST endpoints: \`/parse\`, \`/search\`, and \`/score\`.
- Deploy locally using Docker or to GCP using Cloud Run or GKE.

---

## Project structure
```bash
cv-rag-system/
├── app/
│   ├── main.py                # FastAPI application
│   ├── api/                   # Route definitions
│   │   ├── parse.py
│   │   ├── search.py
│   │   └── score.py
│   ├── services/              # Core logic
│   │   ├── parser.py
│   │   ├── embedder.py
│   │   ├── scorer.py
│   │   └── searcher.py
│   └── utils/
│       └── helpers.py
├── tests/
│   └── test_parse.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.template
├── postman_collection.json
```

---

## Setup

### Prerequisites

- Python 3.9+
- pip
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

Start the development server:

```bash
uvicorn app.main:app --reload
```

Once the server is running, visit \`http://localhost:8000/docs\` to access the interactive API documentation.

---

## Endpoints

### POST `/parse`

Uploads a CV in PDF format, parses the content using the Gemini API, and returns the structured text and its embedding.

### POST `/search`

Accepts a query and returns the top-matching CVs from the vector database based on semantic similarity.

### POST `/score`

Accepts a job description and one or more CVs, returning a relevance score and an explanation of the match.

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

Jameelah Naadirah Mercer  
Founder of [Jua Docs](https://www.juadocs.com)  
[LinkedIn](https://www.linkedin.com/in/jameelahmercer)
EOF


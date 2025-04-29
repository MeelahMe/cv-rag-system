# Gemini-Powered CV Retrieval System

A multilingual, vector-based retrieval system for semantically searching CVs using Google's Gemini API. This project combines FastAPI, Docker, and Weaviate to create a scalable backend for parsing, embedding, storing, and scoring CV documents.

The system is modular, containerized, and designed for local or cloud deployment.

##  System Design Overview

For a detailed system design of the Multilingual CV RAG system, including architecture diagrams, data flow, scalability considerations, and future improvements, see the [System Design Document](./docs/system_design_overview.md).

## API documentation

You can test the full API using the provided Postman Collection:

- [Download CV RAG System API Postman Collection](./CV%20RAG%20System%20API.postman_collection.json)


Use the `cv-rag-system-local` Postman environment with your `base_url` and `api_key` variables configured.

---

## Features

- Parse and embed CVs in English, Arabic, and Spanish using the Gemini API
- Store embeddings with metadata in a Weaviate vector database
- Perform semantic search with optional metadata filtering
- Score job descriptions against CVs to assess relevance
- Modular architecture with clear separation of API routes, services, and utilities
- Local development using Docker Compose
- Seed database with realistic fake CVs for testing and demonstrations

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
│   ├── scripts/               # Development scripts (e.g., seeding)
│   │   └── seed.py
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

To run fully conntainerized (FastAPI + Weaviate):

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

## Seeding the database with Fake CVs

This project includes a Faker-powered seeding script to generate realistic CV data for testing and demo purposes.

### Run the seeding script

Ensure your API server is running, then execute:

```bash
python app/scripts/seed.py
```
The script will insert multiple realistic CVs into the database automatically via the API.

You can configure the number of CVs seeded by editing `num_cvs` inside `seed.py`.

## Local development workflow

## Full local testing

1. Start the API and vector database:

```bash
docker-compose down -v
docker-compose up --build
```

2. In a second terminal, run end-to-end tests:

```bash
./test_features.sh
```
3. Seed sample data:

```bash
./bulk_insert.sh
python app/scripts/seed.py
```
4. Explore API functionality via Postman or browser:

Visit `http://localhost:8000/docs`

---

## Troubleshooting

### Error: `Form data requires "python-multipart" to be installed`

Install the required package:

```bash
pip install python-multipart
```

### Error: `Connection Refused`

Ensure that the FastAPI server is running and accessible at` http://localhost:8000`.

### Error: `Invalid or missing API key`

Verify that the `x-api-key` header is set correctly in your Postman requests.

---

## Future Improvements

- Bulk ingestion optimization (async batch inserts)
- Frontend interface for CV search and scoring
- Enhanced scoring explanation (natural language output)
- Public deployment on GCP Cloud Run

---

## Author

Jameelah Mercer  
[LinkedIn](https://www.linkedin.com/in/jameelahmercer)


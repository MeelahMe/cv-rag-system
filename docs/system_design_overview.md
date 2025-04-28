# Multilingual CV RAG System: System Design Overview

## Overview

This project is a multilingual Retrieval-Augmented Generation (RAG) system built for parsing, embedding, semantically searching, and scoring CVs. It integrates FastAPI services with Google Gemini API embeddings and a Weaviate vector database. The system is modular, scalable, and designed with real-world backend engineering, security, and observability principles in mind.

The goal is to create a fast, secure, and extensible platform for multilingual CV ingestion, semantic retrieval, and job fit scoring.

---

## Architecture Overview

```
User -> FastAPI API Gateway -> Core Services
    - CV Ingestion Service
    - Semantic Search Service
    - Scoring Service
    - Language Detection Service
  |
  -> Weaviate Vector Database
  -> (Optional) Object Storage for CV files
Logging + Monitoring Layer
Authentication Middleware (API Key-Based)
```

Each major function is isolated into its own service to ensure separation of concerns, ease of scaling, and maintainability.

---

## Core Components

| Component | Purpose |
|:---|:---|
| **FastAPI Gateway** | Receives and routes all incoming API requests |
| **CV Ingestion Service** | Parses text/PDFs, detects language, generates embeddings |
| **Semantic Search Service** | Handles user queries and returns top CV matches |
| **Scoring Service** | Compares a job description against a specific CV semantically |
| **Language Detection Service** | Detects and tags the input language of CVs |
| **Authentication Layer** | Validates API keys and protects all endpoints |
| **Logging and Monitoring** | Captures system metrics, errors, and latency measurements |

---

## Data Flow

### CV Insertion Workflow
1. User uploads a CV to `/insert-cv` or `/bulk-insert-cv`.
2. System extracts text and detects the language.
3. Text is embedded using Google Gemini API.
4. Embeddings and metadata are stored in Weaviate.

### Semantic Search Workflow
1. User submits a search query to `/search`.
2. Query is embedded via Gemini.
3. Weaviate searches for nearest neighbors based on vector similarity.
4. Top matching CVs are returned with metadata.

### Scoring Workflow
1. User submits a job description and CV ID to `/score`.
2. System computes semantic similarity between job description and selected CV.
3. A relevance score is returned.

---

## Key Design Decisions

| Area | Decision | Rationale |
|:---|:---|:---|
| **Framework** | FastAPI | Fast async support, ideal for microservice APIs |
| **Embedding Model** | Google Gemini API | State-of-the-art multilingual embeddings |
| **Vector Storage** | Weaviate | Designed for high-performance vector search with metadata filtering |
| **Authentication** | API Key Middleware | Lightweight, fast to implement for controlled access |
| **Deployment** | Dockerized services, deployable on GCP or AWS | Ease of scaling, portability |
| **Monitoring** | Custom logging of latency and ingestion rates | Early bottleneck detection, operational insights |

---

## Scalability and Performance Considerations

- **Batch Processing**: Bulk ingestion endpoints allow handling thousands of CVs in one job.
- **Stateless APIs**: APIs are stateless to allow easy horizontal scaling.
- **Search Latency**: Weaviate ensures retrievals within ~100ms for semantic queries.
- **Observability**: Logs request types, durations, and errors to aid monitoring.
- **Cloud Native**: Optimized for containerized cloud deployments.

---

## Security Considerations

- **API Key Authentication**: Basic protection for all endpoints.
- **Input Validation**: Validate all incoming payloads to prevent injection attacks.
- **Service Isolation**: Each service handles its own errors and doesn't expose unnecessary information.
- **Future Enhancements**: OAuth2 integration and rate-limiting for production-grade deployments.

---

## Future Improvements

- Add **rate limiting** per user/IP for public endpoints.
- Integrate **Celery + Redis** for asynchronous batch processing jobs.
- Expand **file format support** (DOCX, ODT).
- Build **admin dashboard** to visualize search analytics and scoring patterns.
- Enhance **explainability** of scores with retrieved key phrases.

---

## Conclusion

This system is designed to be practical, modular, and extensible — demonstrating real-world backend architecture, DSA principles applied in service design (e.g., nearest neighbor search), multilingual ML integration, and production-readiness. It balances clean engineering with a focus on deployment, security, and user-centric features.

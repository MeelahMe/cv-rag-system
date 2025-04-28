import time
import weaviate
import os
from requests.exceptions import ConnectionError
from app.services.embedder import generate_embedding

VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "http://weaviate:8080")

def connect_to_weaviate(max_retries=20, wait_seconds=3):
    for attempt in range(max_retries):
        try:
            client = weaviate.Client(
                url=VECTOR_DB_HOST,
                additional_headers={"Content-Type": "application/json"}
            )
            if client.is_ready():
                print("Connected to Weaviate.")
                return client
        except Exception:
            print(f"Attempt {attempt + 1}: Weaviate not ready. Retrying in {wait_seconds} seconds...")
            time.sleep(wait_seconds)
    raise RuntimeError("Could not connect to Weaviate after multiple retries.")

client = connect_to_weaviate()

def init_schema():
    class_obj = {
        "class": "CV",
        "description": "A parsed CV document",
        "vectorizer": "none",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "language", "dataType": ["string"]},
            {"name": "skills", "dataType": ["string[]"]},
            {"name": "job_title", "dataType": ["string"]},
            {"name": "years_experience", "dataType": ["number"]}
        ]
    }
    if not client.schema.contains({"class": "CV"}):
        client.schema.create_class(class_obj)
        print("CV class created.")
    else:
        print("CV class already exists.")

def insert_cv(text, embedding, metadata):
    client.data_object.create(
        data_object={**metadata, "text": text},
        class_name="CV",
        vector=embedding
    )

def insert_cvs_bulk(cvs):
    objects = []
    for cv in cvs:
        embedding = generate_embedding(cv.text)
        metadata = {
            "language": cv.language,
            "skills": cv.skills,
            "job_title": cv.job_title,
            "years_experience": cv.years_experience
        }
        objects.append({
            "class": "CV",
            "properties": {**metadata, "text": cv.text},
            "vector": embedding
        })
    with client.batch as batch:
        batch.batch_size = 20
        for obj in objects:
            batch.add_data_object(
                obj["properties"],
                obj["class"],
                vector=obj["vector"]
            )

def search_cvs(query_embedding, top_k=5, filters=None):
    """
    Perform a vector search against stored CVs, with optional metadata filtering.
    """
    query = client.query.get("CV", [
        "text",
        "language",
        "skills",
        "job_title",
        "years_experience",
        "_additional { distance }"
    ]).with_near_vector({
        "vector": query_embedding
    }).with_limit(top_k)

    if filters:
        where_clause = build_where_filter(filters)
        if where_clause:
            query = query.with_where(where_clause)

    response = query.do()

    raw_results = response.get("data", {}).get("Get", {}).get("CV", [])

    results = []
    for item in raw_results:
        distance = item.get("_additional", {}).get("distance")
        similarity_score = 1.0 - distance if distance is not None else None
        result = {
            "text": item.get("text"),
            "language": item.get("language"),
            "skills": item.get("skills"),
            "job_title": item.get("job_title"),
            "years_experience": item.get("years_experience"),
            "score": similarity_score
        }
        results.append(result)

    return results

def build_where_filter(filters):
    """
    Build a Weaviate 'where' filter from a dictionary of filter conditions.
    """
    clauses = []

    if "language" in filters:
        clauses.append({
            "path": ["language"],
            "operator": "Equal",
            "valueString": filters["language"]
        })

    if "min_years_experience" in filters:
        clauses.append({
            "path": ["years_experience"],
            "operator": "GreaterThanEqual",
            "valueNumber": filters["min_years_experience"]
        })

    if "skills" in filters:
        clauses.append({
            "path": ["skills"],
            "operator": "ContainsAny",
            "valueTextArray": filters["skills"]
        })

    if "job_title" in filters:
        clauses.append({
            "path": ["job_title"],
            "operator": "Equal",
            "valueString": filters["job_title"]
        })

    if not clauses:
        return None

    return {
        "operator": "And",
        "operands": clauses
    }

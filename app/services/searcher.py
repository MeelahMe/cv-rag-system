import time
import weaviate
import os

VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "http://cv-rag-vector-db:8080")

def connect_to_weaviate(max_retries=20, wait_seconds=3):
    """
    Attempt to connect to Weaviate, retrying until it is ready or the maximum number of retries is reached.
    """
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

def init_schema():
    """
    Initialize the schema for the CV class in Weaviate if it does not already exist.
    """
    client = connect_to_weaviate()
    
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
    """
    Insert a CV object with its embedding and metadata into the Weaviate database.
    """
    client = connect_to_weaviate()
    
    client.data_object.create(
        data_object={**metadata, "text": text},
        class_name="CV",
        vector=embedding
    )

def search_cvs(query_embedding, top_k=5):
    """
    Perform a vector search against stored CVs and return the top K results with metadata.
    """
    client = connect_to_weaviate()

    response = (
        client.query
        .get("CV", ["text", "language", "skills", "job_title", "years_experience"])
        .with_near_vector({"vector": query_embedding})
        .with_limit(top_k)
        .do()
    )

    return response.get("data", {}).get("Get", {}).get("CV", [])

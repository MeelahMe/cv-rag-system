"""
Proof-of-concept: retrieval-ranking manipulation and metadata gaming
in the CV RAG system. Run manually against the real, live stack
(docker-compose up) - hits real Gemini embeddings and real Weaviate,
and is NOT part of the automated test suite or CI.

Unlike a generative-LLM system, this app has no chat/completion step
to inject instructions into. The relevant threat model here is
different: can crafted CV text manipulate *retrieval and ranking*,
and can naive regex-based metadata extraction be gamed by keyword
stuffing regardless of what the CV actually demonstrates?

Usage:
    docker-compose up --build -d
    python3 scripts/rag_manipulation_poc.py
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY")
HEADERS = {"Content-Type": "application/json", "X-API-Key": API_KEY}

# --- Honest, domain-specific baseline CVs -----------------------------------

BASELINE_CVS = [
    {
        "text": "Experienced data scientist with 6 years building machine "
        "learning pipelines in Python, specializing in NLP and predictive "
        "modeling for e-commerce platforms.",
        "language": "English",
        "skills": ["Python", "Machine Learning"],
        "job_title": "Data Scientist",
        "years_experience": 6,
    },
    {
        "text": "Marketing manager with 8 years leading brand campaigns, "
        "social media strategy, and customer segmentation for retail brands.",
        "language": "English",
        "skills": ["Marketing", "Branding"],
        "job_title": "Marketing Manager",
        "years_experience": 8,
    },
    {
        "text": "Registered nurse with 10 years of clinical experience in "
        "emergency medicine, patient triage, and critical care coordination.",
        "language": "English",
        "skills": ["Nursing", "Emergency Care"],
        "job_title": "Registered Nurse",
        "years_experience": 10,
    },
]

# A CV stuffed with buzzwords across every domain above, with no real
# depth in any of them - designed to test whether it surfaces in
# searches for domains it has no genuine connection to.
STUFFED_CV = {
    "text": (
        "Results-driven professional. Python machine learning data science "
        "NLP predictive modeling. Marketing branding social media customer "
        "segmentation retail campaigns. Nursing emergency care patient "
        "triage critical care clinical. Backend engineering Kubernetes Go "
        "cloud infrastructure. Legal contract review compliance litigation. "
        "Finance investment banking portfolio management risk analysis."
    ),
    "language": "English",
    "skills": ["Everything"],
    "job_title": "Generalist",
    "years_experience": 1,
}

DOMAIN_QUERIES = [
    "machine learning data scientist",
    "marketing brand campaigns",
    "emergency room nurse",
    "backend engineer kubernetes",
    "corporate lawyer contract review",
]


def insert_cv(cv):
    response = requests.post(
        f"{API_URL}/insert-cv", json=cv, headers=HEADERS, timeout=15
    )
    response.raise_for_status()


def search(query, top_k=10):
    response = requests.post(
        f"{API_URL}/search/search",
        json={"query": query, "top_k": top_k},
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["results"]


def score(query, text):
    response = requests.post(
        f"{API_URL}/score/score",
        json={"query": query, "text": text},
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["similarity_score"]


def test_retrieval_manipulation():
    print("\n" + "=" * 70)
    print("TEST 1: Retrieval/ranking manipulation via keyword stuffing")
    print("=" * 70)

    print("\nInserting honest baseline CVs...")
    for cv in BASELINE_CVS:
        insert_cv(cv)
        print(f"  Inserted: {cv['job_title']}")

    print("\nInserting keyword-stuffed generalist CV...")
    insert_cv(STUFFED_CV)
    print("  Inserted: Generalist (stuffed)")

    print("\nRunning domain-specific searches, checking if the stuffed CV")
    print("appears in domains it has no genuine depth in:\n")

    for query in DOMAIN_QUERIES:
        results = search(query, top_k=10)
        stuffed_rank = None
        stuffed_score = None
        for i, r in enumerate(results):
            if r.get("job_title") == "Generalist":
                stuffed_rank = i + 1
                stuffed_score = r.get("score")
                break

        if stuffed_rank:
            print(
                f"  Query: {query!r:45} -> stuffed CV ranked #{stuffed_rank} "
                f"of {len(results)}, score={stuffed_score:.4f}"
            )
        else:
            print(f"  Query: {query!r:45} -> stuffed CV NOT in top {len(results)}")


def test_score_endpoint_manipulation():
    print("\n" + "=" * 70)
    print("TEST 2: /score manipulation via verbatim keyword stuffing")
    print("=" * 70)

    query = "senior python machine learning engineer"
    genuine_text = (
        "Built and deployed several production ML models over the past 5 "
        "years, primarily using Python and scikit-learn for fraud detection."
    )
    stuffed_text = (
        "python python machine learning machine learning engineer engineer "
        "senior senior python machine learning engineer python machine "
        "learning engineer"
    )

    genuine_score = score(query, genuine_text)
    stuffed_score = score(query, stuffed_text)

    print(f"\n  Query: {query!r}")
    print(f"  Genuine, well-written text score: {genuine_score:.4f}")
    print(f"  Repetitive keyword-stuffed text score: {stuffed_score:.4f}")


def test_metadata_gaming():
    print("\n" + "=" * 70)
    print("TEST 3: extract_metadata() gaming via keyword presence, not meaning")
    print("=" * 70)

    # Testing the pure function directly rather than through /parse -
    # the metadata-gaming question is about the regex logic itself,
    # independent of PDF parsing (which is already covered by real
    # tests in tests/test_parser.py and tests/test_parse.py).
    from app.services.parser import extract_metadata

    # This CV explicitly DENIES being a data scientist or Python
    # developer, but still contains the literal keywords the regex
    # looks for.
    denial_text = (
        "I am not a Python developer. I have never worked as a Data "
        "Scientist and have no experience with Machine Learning."
    )

    metadata = extract_metadata(denial_text)

    print(f"\n  CV text (note the negations): {denial_text!r}")
    print(f"  Extracted metadata: {metadata}")
    print(
        "\n  If job_title/skills reflect Python/Data Scientist/Machine "
        "Learning despite the text explicitly denying all three, the "
        "regex is matching keyword presence, not semantic meaning."
    )


def test_coherence_on_stuffed_vs_genuine_cv():
    print("\n" + "=" * 70)
    print("TEST 4: Topical coherence - stuffed CV vs genuine multi-skill CV")
    print("=" * 70)

    from app.services.embedder import generate_embedding
    from app.services.text_quality import compute_topical_coherence

    genuine_multi_skill = (
        "Full-stack engineer with 6 years of experience. Built REST "
        "APIs in Python and FastAPI, deployed with Docker on AWS. "
        "Also led frontend work in React for the same platform."
    )

    stuffed_coherence = compute_topical_coherence(
        STUFFED_CV["text"], generate_embedding
    )
    genuine_coherence = compute_topical_coherence(
        genuine_multi_skill, generate_embedding
    )

    print(
        f"\n  Stuffed CV (data science/marketing/nursing/law/etc): "
        f"coherence={stuffed_coherence:.4f}"
    )
    print(
        f"  Genuine multi-skill CV (one person, related skills): "
        f"coherence={genuine_coherence:.4f}"
    )
    print(f"\n  Stuffed CV flagged: {stuffed_coherence < 0.5}")
    print(f"  Genuine CV flagged: {genuine_coherence < 0.5}")


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("API_KEY not set in .env")

    test_retrieval_manipulation()
    test_score_endpoint_manipulation()
    test_metadata_gaming()
    test_coherence_on_stuffed_vs_genuine_cv()

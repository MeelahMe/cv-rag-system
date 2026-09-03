from unittest.mock import patch


VALID_PAYLOAD = {
    "text": "John Doe is a senior data scientist with 5 years of experience.",
    "language": "English",
    "skills": ["Python", "Machine Learning"],
    "job_title": "Senior Data Scientist",
    "years_experience": 5,
}


def test_insert_cv_success(client, auth_headers):
    with patch(
        "app.api.insert.generate_embedding", return_value=[0.1, 0.2, 0.3]
    ) as mock_embed:
        with patch("app.api.insert.insert_cv", return_value=None) as mock_insert:
            response = client.post(
                "/insert-cv", json=VALID_PAYLOAD, headers=auth_headers
            )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "CV inserted successfully"
    # Single-sentence text short-circuits the coherence check (needs
    # at least 2 sentences to compare against each other).
    assert data["coherence_score"] == 1.0
    assert data["flagged_low_coherence"] is False
    mock_embed.assert_called_once_with(VALID_PAYLOAD["text"])
    mock_insert.assert_called_once()


def test_insert_cv_flags_low_topical_coherence(client, auth_headers):
    """
    Multi-sentence text where each sentence embeds to an orthogonal
    (completely unrelated) vector should be flagged as low coherence -
    this simulates a buzzword-stuffed CV covering unrelated domains,
    which lexical_diversity() alone cannot catch since the words
    themselves may all be unique.
    """
    payload = {
        "text": "First sentence about data science. Second sentence "
        "about nursing. Third sentence about corporate law.",
        "language": "English",
        "job_title": "Generalist",
    }

    # Three orthogonal 3D vectors - maximally dissimilar to each other.
    orthogonal_vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

    with patch("app.api.insert.generate_embedding", side_effect=orthogonal_vectors * 2):
        with patch("app.api.insert.insert_cv", return_value=None):
            response = client.post("/insert-cv", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["flagged_low_coherence"] is True
    assert data["coherence_score"] == 0.0


def test_insert_cv_missing_required_field(client, auth_headers):
    payload = {"text": "Test", "language": "English"}  # missing job_title
    response = client.post("/insert-cv", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_insert_cv_embedding_failure_returns_500(client, auth_headers):
    with patch(
        "app.api.insert.generate_embedding", side_effect=RuntimeError("Gemini down")
    ):
        response = client.post("/insert-cv", json=VALID_PAYLOAD, headers=auth_headers)

    assert response.status_code == 500
    assert "Gemini down" in response.json()["detail"]


def test_bulk_insert_cv_success(client, auth_headers):
    payload = {"cvs": [VALID_PAYLOAD, VALID_PAYLOAD]}
    with patch("app.api.insert.insert_cvs_bulk", return_value=None) as mock_bulk:
        response = client.post("/bulk-insert-cv", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"message": "2 CVs inserted successfully"}
    mock_bulk.assert_called_once()


def test_bulk_insert_cv_failure_returns_500(client, auth_headers):
    payload = {"cvs": [VALID_PAYLOAD]}
    with patch(
        "app.api.insert.insert_cvs_bulk", side_effect=RuntimeError("Weaviate down")
    ):
        response = client.post("/bulk-insert-cv", json=payload, headers=auth_headers)

    assert response.status_code == 500
    assert "Weaviate down" in response.json()["detail"]

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
    assert response.json() == {"message": "CV inserted successfully"}
    mock_embed.assert_called_once_with(VALID_PAYLOAD["text"])
    mock_insert.assert_called_once()


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

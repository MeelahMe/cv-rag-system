from unittest.mock import patch


def test_search_basic_success(client, auth_headers):
    fake_results = [
        {
            "text": "John Doe is a data scientist.",
            "language": "English",
            "skills": ["Python"],
            "job_title": "Data Scientist",
            "years_experience": 5,
            "score": 0.85,
        }
    ]

    with patch("app.api.search.generate_embedding", return_value=[0.1, 0.2, 0.3]):
        with patch(
            "app.api.search.search_cvs", return_value=fake_results
        ) as mock_search:
            response = client.post(
                "/search/search",
                json={"query": "machine learning", "top_k": 5},
                headers=auth_headers,
            )

    assert response.status_code == 200
    assert response.json() == {"results": fake_results}
    mock_search.assert_called_once()


def test_search_filters_passed_through(client, auth_headers):
    with patch("app.api.search.generate_embedding", return_value=[0.1, 0.2, 0.3]):
        with patch("app.api.search.search_cvs", return_value=[]) as mock_search:
            response = client.post(
                "/search/search",
                json={
                    "query": "data scientist",
                    "top_k": 5,
                    "language": "English",
                    "min_years_experience": 3,
                    "skills": ["Python"],
                    "job_title": "Senior Data Scientist",
                },
                headers=auth_headers,
            )

    assert response.status_code == 200
    _, kwargs = mock_search.call_args
    assert kwargs["filters"] == {
        "language": "English",
        "min_years_experience": 3,
        "skills": ["Python"],
        "job_title": "Senior Data Scientist",
    }


def test_search_missing_required_field(client, auth_headers):
    response = client.post("/search/search", json={"top_k": 5}, headers=auth_headers)
    assert response.status_code == 422


def test_search_embedding_failure_returns_500(client, auth_headers):
    with patch(
        "app.api.search.generate_embedding", side_effect=RuntimeError("Gemini down")
    ):
        response = client.post(
            "/search/search", json={"query": "python"}, headers=auth_headers
        )

    assert response.status_code == 500
    assert "Gemini down" in response.json()["detail"]


def test_search_backend_failure_returns_500(client, auth_headers):
    with patch("app.api.search.generate_embedding", return_value=[0.1, 0.2, 0.3]):
        with patch(
            "app.api.search.search_cvs", side_effect=RuntimeError("Weaviate down")
        ):
            response = client.post(
                "/search/search", json={"query": "python"}, headers=auth_headers
            )

    assert response.status_code == 500
    assert "Weaviate down" in response.json()["detail"]

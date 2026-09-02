from unittest.mock import patch


def test_insert_cv_missing_key_returns_401(client):
    response = client.post("/insert-cv", json={
        "text": "Test", "language": "English", "job_title": "Engineer"
    })
    assert response.status_code == 401


def test_insert_cv_wrong_key_returns_401(client):
    response = client.post(
        "/insert-cv",
        json={"text": "Test", "language": "English", "job_title": "Engineer"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_search_missing_key_returns_401(client):
    response = client.post("/search/search", json={"query": "python developer"})
    assert response.status_code == 401


def test_score_missing_key_returns_401(client):
    response = client.post(
        "/score/score", json={"query": "python", "text": "python developer"}
    )
    assert response.status_code == 401


def test_parse_missing_key_returns_401(client):
    response = client.post(
        "/parse/parse", files={"file": ("test.pdf", b"%PDF-1.4 fake", "application/pdf")}
    )
    assert response.status_code == 401


def test_insert_cv_correct_key_passes_auth(client, auth_headers):
    # Mock the real dependencies so this test only proves auth passes,
    # not that embedding/insertion actually works (that's tested
    # separately in test_insert.py).
    with patch("app.api.insert.generate_embedding", return_value=[0.1, 0.2, 0.3]):
        with patch("app.api.insert.insert_cv", return_value=None):
            response = client.post(
                "/insert-cv",
                json={"text": "Test", "language": "English", "job_title": "Engineer"},
                headers=auth_headers,
            )
    assert response.status_code == 200


def test_missing_server_api_key_returns_500(client, monkeypatch):
    """
    If the server itself has no API_KEY configured, verify_api_key
    should fail closed with a clean 500, not silently let requests
    through or crash unhandled.
    """
    monkeypatch.delenv("API_KEY", raising=False)
    response = client.post(
        "/insert-cv",
        json={"text": "Test", "language": "English", "job_title": "Engineer"},
        headers={"X-API-Key": "anything"},
    )
    assert response.status_code == 500
    assert "API_KEY" in response.json()["detail"]

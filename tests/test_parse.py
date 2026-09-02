from unittest.mock import patch


def test_parse_success(client, auth_headers):
    fake_metadata = {
        "language": "en",
        "skills": ["Python"],
        "job_title": "Software Engineer",
        "years_experience": 5,
    }

    with patch("app.api.parse.parser.parse_content", return_value="Some CV text"):
        with patch("app.api.parse.embedder.generate_embedding", return_value=[0.1, 0.2]):
            with patch("app.api.parse.parser.extract_metadata", return_value=fake_metadata):
                with patch("app.api.parse.searcher.insert_cv", return_value=None) as mock_insert:
                    response = client.post(
                        "/parse/parse",
                        files={"file": ("cv.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")},
                        headers=auth_headers,
                    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "CV parsed and stored successfully",
        "metadata": fake_metadata,
    }
    mock_insert.assert_called_once()


def test_parse_rejects_non_pdf_with_clean_error(client, auth_headers):
    """
    parser.parse_content() raises ValueError for non-PDF files. Every
    other route in this API (insert, search, score) catches exceptions
    and returns a clean {"detail": ...} JSON error. This test checks
    that /parse does the same, instead of leaking an unhandled 500.
    """
    response = client.post(
        "/parse/parse",
        files={"file": ("resume.txt", b"just some text", "text/plain")},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]


def test_parse_embedding_failure_returns_clean_500(client, auth_headers):
    with patch("app.api.parse.parser.parse_content", return_value="Some CV text"):
        with patch(
            "app.api.parse.embedder.generate_embedding",
            side_effect=RuntimeError("Gemini down"),
        ):
            response = client.post(
                "/parse/parse",
                files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
                headers=auth_headers,
            )

    assert response.status_code == 500
    assert "Gemini down" in response.json()["detail"]

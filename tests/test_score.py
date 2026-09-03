import math
from unittest.mock import patch

from app.api.score import cosine_similarity


# --- Direct unit tests on the math itself. These specifically guard
# against the bug fixed on 2026-08-30: the original implementation was
# a raw, unnormalized dot product, not real cosine similarity. ---


def test_cosine_similarity_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert math.isclose(cosine_similarity(v, v), 1.0, rel_tol=1e-9)


def test_cosine_similarity_orthogonal_vectors():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert math.isclose(cosine_similarity(a, b), 0.0, abs_tol=1e-9)


def test_cosine_similarity_opposite_vectors():
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert math.isclose(cosine_similarity(a, b), -1.0, rel_tol=1e-9)


def test_cosine_similarity_bounded_regardless_of_magnitude():
    # The old, broken implementation (raw dot product) would return a
    # different result if a vector's magnitude changed, even with the
    # same direction. Real cosine similarity should not.
    a = [1.0, 0.0]
    b = [1.0, 0.0]
    b_scaled = [100.0, 0.0]
    assert math.isclose(
        cosine_similarity(a, b), cosine_similarity(a, b_scaled), rel_tol=1e-9
    )


def test_cosine_similarity_zero_vector_returns_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


# --- API-level tests ---


def test_score_success(client, auth_headers):
    with patch(
        "app.api.score.generate_embedding",
        side_effect=[[1.0, 0.0], [1.0, 0.0]],
    ):
        response = client.post(
            "/score/score",
            json={"query": "python", "text": "python developer"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json() == {"similarity_score": 1.0}


def test_score_missing_required_field(client, auth_headers):
    response = client.post(
        "/score/score", json={"query": "python"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_score_embedding_failure_returns_500(client, auth_headers):
    with patch(
        "app.api.score.generate_embedding", side_effect=RuntimeError("Gemini down")
    ):
        response = client.post(
            "/score/score",
            json={"query": "python", "text": "python developer"},
            headers=auth_headers,
        )

    assert response.status_code == 500
    assert "Gemini down" in response.json()["detail"]

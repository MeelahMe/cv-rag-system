from app.services.searcher import build_where_filter


def test_build_where_filter_returns_none_for_empty_filters():
    assert build_where_filter({}) is None


def test_build_where_filter_single_clause():
    result = build_where_filter({"language": "English"})

    assert result == {
        "operator": "And",
        "operands": [
            {"path": ["language"], "operator": "Equal", "valueString": "English"}
        ],
    }


def test_build_where_filter_combines_multiple_clauses():
    result = build_where_filter(
        {
            "language": "English",
            "min_years_experience": 3,
            "skills": ["Python", "SQL"],
            "job_title": "Data Scientist",
        }
    )

    assert result["operator"] == "And"
    assert len(result["operands"]) == 4

    paths = [clause["path"][0] for clause in result["operands"]]
    assert set(paths) == {"language", "years_experience", "skills", "job_title"}

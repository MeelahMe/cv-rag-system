from app.services.parser import extract_metadata, parse_content


def test_extract_metadata_finds_known_fields():
    text = "Jane is a Data Scientist with 5 years of experience in Python and SQL."
    result = extract_metadata(text)

    assert result["job_title"] == "Data Scientist"
    assert result["years_experience"] == 5
    assert set(result["skills"]) == {"Python", "Sql"}
    assert result["language"] == "en"


def test_extract_metadata_no_matches_returns_defaults():
    text = "This text contains nothing that matches any of the known patterns."
    result = extract_metadata(text)

    assert result["job_title"] == "Unknown"
    assert result["years_experience"] == 0
    assert result["skills"] == []


def test_extract_metadata_case_insensitive():
    text = "expert in python and docker, software engineer role"
    result = extract_metadata(text)

    assert result["job_title"] == "Software Engineer"
    assert set(result["skills"]) == {"Python", "Docker"}


def test_extract_metadata_dedupes_repeated_skills():
    text = "Python developer. Python. Python again, still Python."
    result = extract_metadata(text)

    assert result["skills"] == ["Python"]


def test_parse_content_rejects_non_pdf_filename():
    import pytest

    with pytest.raises(ValueError, match="Only PDF files are supported"):
        parse_content(b"irrelevant content", "resume.docx")


def test_extract_metadata_ignores_negated_skills():
    text = (
        "I am not a Python developer. I have never worked as a Data "
        "Scientist and have no experience with Machine Learning."
    )
    result = extract_metadata(text)

    assert result["skills"] == []
    assert result["job_title"] == "Unknown"


def test_extract_metadata_still_matches_genuine_mentions():
    text = "I am a Python developer with strong SQL skills, currently a Data Scientist."
    result = extract_metadata(text)

    assert "Python" in result["skills"]
    assert "Sql" in result["skills"]
    assert result["job_title"] == "Data Scientist"

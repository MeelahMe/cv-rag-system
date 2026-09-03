from PyPDF2 import PdfReader
import io
import re


def parse_content(content: bytes, filename: str) -> str:
    """
    Extract text content from a PDF file.
    """
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text.strip()


NEGATION_WORDS = {"not", "no", "never", "without", "nor"}


def _is_negated(text: str, match_start: int, window: int = 5) -> bool:
    """
    Simple negation-scope heuristic: checks whether a negation word
    appears within `window` words immediately before a matched keyword.
    Not full NLP negation detection - just enough to catch the clear,
    common cases like "not a Python developer" or "never worked as a
    Data Scientist", which the original regex had no defense against
    at all (it would tag both as genuine matches).
    """
    preceding_text = text[:match_start].lower()
    preceding_words = re.findall(r"\b\w+\b", preceding_text)
    nearby_words = preceding_words[-window:]
    return any(w in NEGATION_WORDS or w.endswith("nt") for w in nearby_words)


def extract_metadata(text: str) -> dict:
    """
    Extracts basic metadata like language, skills, job title, and experience from the CV text.
    Replace these rules with more robust NLP as needed.

    Negation-aware: a keyword preceded by a negation word (e.g. "not a
    Python developer") is excluded rather than counted as a match.
    """
    skill_pattern = re.compile(
        r"\b(Python|Java|SQL|FastAPI|Docker|TensorFlow)\b", re.IGNORECASE
    )
    skills = [
        m.group(0)
        for m in skill_pattern.finditer(text)
        if not _is_negated(text, m.start())
    ]

    job_title_pattern = re.compile(
        r"\b(Software Engineer|Data Scientist|DevOps Engineer)\b", re.IGNORECASE
    )
    job_title = "Unknown"
    for m in job_title_pattern.finditer(text):
        if not _is_negated(text, m.start()):
            job_title = m.group(0).title()
            break

    experience_match = re.search(r"(\d+)\s+years?", text)

    return {
        "language": "en",  # You can later use a library to auto-detect this
        "skills": list(set(skill.capitalize() for skill in skills)),
        "job_title": job_title,
        "years_experience": int(experience_match.group(1)) if experience_match else 0,
    }

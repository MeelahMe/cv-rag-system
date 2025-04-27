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

def extract_metadata(text: str) -> dict:
    """
    Extracts basic metadata like language, skills, job title, and experience from the CV text.
    Replace these rules with more robust NLP as needed.
    """
    # Dummy rules (you can improve this with real NLP later)
    skills = re.findall(r"\b(Python|Java|SQL|FastAPI|Docker|TensorFlow)\b", text, re.IGNORECASE)
    job_title_match = re.search(r"\b(Software Engineer|Data Scientist|DevOps Engineer)\b", text, re.IGNORECASE)
    experience_match = re.search(r"(\d+)\s+years?", text)

    return {
        "language": "en",  # You can later use a library to auto-detect this
        "skills": list(set(skill.capitalize() for skill in skills)),
        "job_title": job_title_match.group(0) if job_title_match else "Unknown",
        "years_experience": int(experience_match.group(1)) if experience_match else 0
    }

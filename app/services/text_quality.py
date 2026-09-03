import math
import re
from typing import Callable, List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Moved here from app/api/score.py since it's now shared by both the
    /score endpoint and topical coherence detection below.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def lexical_diversity(text: str) -> float:
    """
    Ratio of unique words to total words. Low values indicate
    repetitive text - e.g. "python python machine learning machine
    learning" - which can be used to artificially inflate similarity
    scores against embedding-based systems, since repetition biases
    the resulting vector toward those repeated terms.
    """
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return 1.0
    return len(set(words)) / len(words)


def is_likely_stuffed(text: str, threshold: float = 0.5, min_words: int = 15) -> bool:
    """
    Flags text as likely keyword-stuffed. Only applies the check to
    text long enough for the ratio to be meaningful - short, naturally
    repetitive phrases ("Python, Python developer") shouldn't trip
    this on a legitimate short bio.
    """
    words = re.findall(r"\b\w+\b", text.lower())
    if len(words) < min_words:
        return False
    return lexical_diversity(text) < threshold


def split_into_sentences(text: str) -> List[str]:
    """
    Naive sentence splitting on ., !, and ?. Good enough for detecting
    topic shifts between sentences - doesn't need to be linguistically
    perfect for that purpose.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 0]


def compute_topical_coherence(
    text: str, embed_fn: Callable[[str], List[float]], min_sentences: int = 2
) -> float:
    """
    Splits text into sentences, embeds each one, and returns the
    MINIMUM pairwise cosine similarity between them (not the average -
    see note below).

    Rationale: lexical_diversity() catches literal word repetition,
    but not a CV stuffed with buzzwords from many unrelated domains -
    that kind of text has almost no repeated words, so it passes the
    diversity check cleanly, yet its sentences are semantically
    unrelated to each other. A genuine CV, even one describing
    several skills, should read as coherently about one person's
    background; its sentences should be reasonably similar to each
    other in embedding space. A buzzword-salad CV covering data
    science, marketing, nursing, backend engineering, and law in
    consecutive sentences should not.

    Uses the minimum, not the average, pairwise similarity. An
    earlier version used the average, but testing showed it was too
    diluted to reliably separate stuffed from genuine text: generic
    "professional CV language" (years of experience, responsible for,
    etc.) gives all sentences a baseline similarity to each other
    regardless of actual topic, which pulls the average up across the
    board. The minimum is far more sensitive - it drops sharply the
    moment even one sentence is on a genuinely unrelated topic, which
    matches the actual shape of the stuffed-CV attack (many different
    domains crammed together) much better than an average does.

    Requires one embedding call per sentence - meaningfully more
    expensive than the other checks in this module. Intended for
    single-CV endpoints (insert-cv, parse), not bulk insert.

    Returns 1.0 (maximally coherent) if there aren't enough sentences
    to meaningfully measure incoherence.
    """
    sentences = split_into_sentences(text)
    if len(sentences) < min_sentences:
        return 1.0

    embeddings = [embed_fn(s) for s in sentences]

    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarities.append(cosine_similarity(embeddings[i], embeddings[j]))

    if not similarities:
        return 1.0

    return min(similarities)

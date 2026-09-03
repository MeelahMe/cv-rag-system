# Security Finding: Retrieval Manipulation and Metadata Gaming in the CV RAG Pipeline

## Summary

This system has no generative LLM step: `/parse`, `/insert-cv`, `/search`, and
`/score` only ever call Gemini's *embedding* endpoint, never a chat/completion
endpoint. There is no system prompt to hijack and no generated text an
attacker could manipulate, because nothing here generates text. Classic
prompt injection (getting a model to follow attacker instructions instead of
its system prompt) does not apply to this architecture.

The relevant risk instead is specific to retrieval and matching systems:
can crafted input text manipulate *ranking, scoring, and metadata
extraction* rather than *generated output*? Testing found three real,
distinct issues. Two were fixed and the fixes were proven with live
before/after data. The third (retrieval-ranking manipulation) was confirmed
real but not fixed; a mitigation attempt for it (topical coherence
detection) was tried with two different methods and both were inconclusive,
which is documented honestly below rather than presented as a success.

## Threat model

- **Attacker**: anyone able to submit a CV via `/insert-cv` or `/parse` -
  in this project gated behind API key auth, but in the design this is
  based on (a hiring/candidate-matching tool), CVs are inherently
  attacker-influenced content: the candidate being scored has every
  incentive to write their own CV in whatever way ranks best, whether or
  not that reflects their real qualifications.
- **Attack surface**: the free-text `text` field on CVs, and the `query`/
  `text` fields on `/score`.
- **Goals tested**:
  1. Get an unqualified CV to rank highly for searches it has no genuine
     relevance to (retrieval manipulation)
  2. Get a `/score` similarity result inflated through text that isn't
     actually more relevant, just repetitive (score manipulation)
  3. Get `extract_metadata()` to tag a CV with skills/job titles the CV
     text explicitly denies having (metadata gaming)

## Methodology

- Real calls against the live stack: Gemini `gemini-embedding-001` via the
  current `google-genai` SDK, and a real Weaviate instance via
  `docker-compose up`.
- Script: `scripts/rag_manipulation_poc.py` (manual, not part of the
  automated test suite or CI - hits real, billable embedding calls).
- Four honest baseline CVs across distinct, unrelated domains (data
  science, marketing, nursing, and later backend/legal via search
  queries), inserted first.
- One deliberately unqualified "keyword-stuffed" CV covering many
  unrelated domains with almost no repeated words, inserted alongside
  the honest baselines.
- Domain-specific search queries run against the full set, checking
  where the stuffed CV ranked.
- A separate direct test of `/score` with genuine vs. literally
  repetitive text.
- A separate direct test of `extract_metadata()` with text that
  explicitly denies having specific skills.
- After building mitigations, all three were re-run to measure actual
  before/after impact, not just assumed improvement.

## Finding 1: Retrieval-ranking manipulation (confirmed, unresolved)

A CV with essentially no genuine qualifications in any domain - just
buzzwords from data science, marketing, nursing, backend engineering, and
law crammed into one paragraph - ranked **#1 of 8** for both "backend
engineer kubernetes" and "corporate lawyer contract review," domains it
has zero real connection to. It ranked #2-3 of 8 for every other query
tested.

This is a real problem for a system whose whole purpose is helping
someone find genuinely relevant candidates: an unqualified but
well-buzzworded CV can outrank or crowd out genuinely qualified ones.

**Status: confirmed, not fixed.** A mitigation attempt is documented in
"Failed mitigation attempt" below. Fully solving this is a genuinely hard,
open problem - it's structurally the same cat-and-mouse dynamic as SEO
spam versus search engines - and not something a lightweight fix reliably
closes.

## Finding 2: `/score` inflation via literal repetition (confirmed, fixed)

Repetitive, low-effort text ("python python machine learning machine
learning engineer engineer...") scored **0.9127** against a relevant
query, while genuine, well-written, actually relevant text scored only
**0.7054** - the scoring rewarded repetition over quality, nearly the
opposite of what a similarity score should do.

**Root cause:** cosine similarity on raw embeddings has no defense against
an attacker simply repeating query-relevant terms; embedding models can be
biased toward repeated tokens.

**Fix:** `app/services/text_quality.py` adds `lexical_diversity()` (ratio
of unique to total words) and `is_likely_stuffed()` (flags text below a
threshold, only for text long enough that the ratio is meaningful).
`/score` now halves the similarity score for flagged text and reports
`flagged_low_diversity` in the response.

**Verified after fix:** the same repetitive text now scores **0.4563**,
correctly below the genuine text's 0.7054. Covered by
`tests/test_score.py::test_score_flags_and_penalizes_repetitive_text` and
confirmed live in `scripts/rag_manipulation_poc.py`.

## Finding 3: Metadata gaming via negation-blindness (confirmed, fixed)

`extract_metadata()` used `re.IGNORECASE` regex matching with zero
understanding of negation. A CV reading *"I am not a Python developer. I
have never worked as a Data Scientist and have no experience with Machine
Learning"* was tagged with `skills: ["Python"]` and `job_title: "Data
Scientist"` - the exact opposite of what the text says.

**Root cause:** the regex only checks whether a keyword appears anywhere
in the text, with no semantic or syntactic context around it.

**Fix:** added a simple negation-scope heuristic (`_is_negated()` in
`app/services/parser.py`) - checks whether a negation word ("not", "no",
"never", "without", "nor") appears within a 5-word window before a
matched keyword, and excludes the match if so. Not full NLP negation
detection, but enough to catch the clear, common cases.

**Verified after fix:** the same denial text now correctly produces
`skills: []`, `job_title: "Unknown"`. Confirmed the fix doesn't
over-correct: genuine mentions ("I am a Python developer... currently a
Data Scientist") still match correctly. Covered by
`tests/test_parser.py::test_extract_metadata_ignores_negated_skills` and
`test_extract_metadata_still_matches_genuine_mentions`, and confirmed live.

## Failed mitigation attempt: topical coherence detection

Given Finding 1 (retrieval manipulation) remained unresolved, an attempt
was made to detect it directly: split CV text into sentences, embed each
one, and measure pairwise similarity between them. The hypothesis: a
genuine multi-skill CV should read coherently about one person's real
background (its sentences should be reasonably similar to each other in
embedding space), while a buzzword-stuffed CV covering unrelated domains
should not.

**First attempt (average pairwise similarity):** stuffed CV scored 0.5794,
a genuine multi-skill CV scored 0.6031. Directionally correct (stuffed was
lower) but the gap was too small to set a reliable threshold; neither
crossed a reasonable flagging line.

**Second attempt (minimum pairwise similarity, on the theory that
averaging diluted the signal):** stuffed CV scored 0.5421, genuine scored
0.5917. Same story - directionally correct, still too close together to
reliably separate.

**Conclusion:** both approaches showed the same underlying limitation, not
a problem with the aggregation method. Gemini's embedding model appears to
treat all "professional CV-style sentences" as broadly similar to each
other regardless of actual topic - shared stylistic and domain-general
vocabulary ("years of experience," "responsible for") pulls sentence
embeddings closer together than topic content alone would suggest. This
made sentence-level embedding similarity too weak a signal, on its own, to
reliably distinguish genuine multi-domain expertise from cross-domain
buzzword stuffing.

This is left in the codebase (`compute_topical_coherence()` in
`app/services/text_quality.py`, wired into `/insert-cv` as
`coherence_score`/`flagged_low_coherence` in the response) as advisory
data, not as a working detector - the threshold isn't set to actually
block or reliably flag anything right now. Retrieval-ranking manipulation
(Finding 1) remains an open problem.

## Known limitations of this testing

- **Small sample sizes.** A handful of CVs and queries were tested, not a
  large labeled dataset. The findings show real, reproducible behavior on
  these examples, not statistically rigorous rates.
- **Single embedding model.** Only `gemini-embedding-001` was tested.
  Findings, especially the coherence-detection failure, may not generalize
  to other embedding models.
- **Not automated.** This testing is a manual script (`scripts/
  rag_manipulation_poc.py`), not part of CI. A future change to scoring or
  metadata logic would not be automatically regression-tested against
  these specific attack scenarios (the *unit-level* regression tests for
  the two fixed issues do run in CI, in `tests/test_score.py` and
  `tests/test_parser.py`).
- **Non-deterministic embeddings across runs.** Exact scores shift
  slightly between runs (e.g. the coherence scores differed slightly
  between the two mitigation attempts even accounting for the method
  change) - the relative ordering and conclusions held up consistently,
  but exact numbers shouldn't be treated as fixed constants.

## Bugs found incidentally during this testing

Live testing against the real stack (rather than only mocked unit tests)
surfaced a real gap the mocked tests had missed: `app/api/parse.py`'s
error handling only caught `ValueError`, but a `.pdf`-named file with
genuinely malformed content raises `PyPDF2.errors.PdfReadError`, a
different exception class, which slipped through and crashed unhandled.
Fixed by broadening the `except` clause and adding
`tests/test_parse.py::test_parse_rejects_malformed_pdf_with_clean_error`
as a regression test. This is a good example of why testing against a
real running system, not just mocks, matters: the mocked test suite looked
complete but missed this entirely.

## Recommended next steps

- Investigate a real classifier or LLM-judged approach for detecting
  cross-domain topic stuffing, since embedding similarity alone proved
  insufficient here.
- Test whether a different embedding model shows a stronger coherence
  signal than `gemini-embedding-001` did.
- Extend metadata-gaming testing beyond negation to other manipulation
  patterns (e.g. exaggeration, misleading context).
- Add the manual PoC script's scenarios as an automated adversarial
  regression suite in CI, similar to the recommendation on
  `llm-backend-intelligence-system`.

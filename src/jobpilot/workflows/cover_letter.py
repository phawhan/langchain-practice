"""Reflection pattern: write -> critique -> revise, until the critic approves or we run out of revisions.

Code checks what code can check (word count). The LLM critic checks meaning (made-up claims).
"""
from pydantic import BaseModel, Field

from jobpilot.llm import get_chat_model
from jobpilot.models import Candidate, Job

MAX_WORDS = 170  # prompt asks for 150; small buffer before we call it a problem

WRITER_PROMPT = """Write a cover letter of at most 150 words for this candidate and job.
Rules:
- Use ONLY facts from the candidate profile. Never claim skills, years, or projects that are not in it.
- If the job needs a skill the candidate lacks, say they are actively learning it. Do not pretend.
- Connect 2-3 of the candidate's real skills to the job's needs. No generic filler.
Return only the letter text."""

CRITIC_PROMPT = """You review cover letters for honesty. Compare the letter with the candidate profile and the job.
- unsupported_claims: every claim in the letter that the profile does NOT support (skills, years, projects, results).
- missed_strengths: job requirements the candidate HAS but the letter does not mention.
Use empty lists when there are none."""


class CoverLetterReview(BaseModel):
    unsupported_claims: list[str] = Field(description="Claims in the letter that the profile does not support")
    missed_strengths: list[str] = Field(description="Job requirements the candidate has but the letter ignores")


class CoverLetterResult(BaseModel):
    letter: str
    approved: bool
    revisions: int
    reviews: list[dict]  # what the critic found in each round, for transparency and debugging


def _facts(candidate: Candidate, job: Job) -> str:
    return f"CANDIDATE PROFILE:\n{candidate.model_dump_json()}\n\nJOB:\n{job.model_dump_json()}"


def generate_reviewed_cover_letter(candidate: Candidate, job: Job, max_revisions: int = 2) -> CoverLetterResult:
    writer = get_chat_model(temperature=0.7)  # some creativity for writing
    critic = get_chat_model(thinking=False).with_structured_output(CoverLetterReview)  # strict, typed, fast
    letter = writer.invoke([("system", WRITER_PROMPT), ("user", _facts(candidate, job))]).content
    reviews = []
    for revision in range(max_revisions + 1):
        review = critic.invoke([("system", CRITIC_PROMPT), ("user", f"{_facts(candidate, job)}\n\nLETTER:\n{letter}")])
        blocking = [f"Unsupported claim: {c}" for c in review.unsupported_claims]
        if (words := len(letter.split())) > MAX_WORDS:
            blocking.append(f"Too long: {words} words, limit is 150.")
        suggestions = [f"Mention this real strength: {s}" for s in review.missed_strengths]
        reviews.append({"round": revision + 1, "blocking": blocking, "suggestions": suggestions})
        if not blocking:
            return CoverLetterResult(letter=letter, approved=True, revisions=revision, reviews=reviews)
        if revision == max_revisions:
            break
        feedback = "\n- ".join(blocking + suggestions)
        letter = writer.invoke([
            ("system", WRITER_PROMPT),
            ("user", f"{_facts(candidate, job)}\n\nPREVIOUS LETTER:\n{letter}\n\nFIX THESE PROBLEMS:\n- {feedback}"),
        ]).content
    return CoverLetterResult(letter=letter, approved=False, revisions=max_revisions, reviews=reviews)

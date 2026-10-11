"""Job data access.

The agent's tools only talk to the JobRepository interface. Today it is backed by a JSON file
with keyword search; later it becomes pgvector + hybrid RAG without any change to the agent.
"""
import json
import logging
from pathlib import Path
from typing import Protocol

from jobpilot.models import Job
from jobpilot.security.content_scanner import scan_text

logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "jobs.json"


class JobRepository(Protocol):
    def search(
        self, keywords: str, location: str | None = None, experience_years: int | None = None, limit: int = 5
    ) -> list[Job]: ...

    def get(self, job_id: str) -> Job | None: ...


class InMemoryJobRepository:
    """Keyword search over seed data. Placeholder until the pgvector version."""

    def __init__(self, seed_file: Path = SEED_FILE):
        self._jobs: dict[str, Job] = {}
        self.quarantined: dict[str, list[str]] = {}  # job_id -> rules it broke; waits for human review
        for item in json.loads(seed_file.read_text()):
            job = Job(**item)
            # Ingestion scan (4.9): stop poisoned postings at the door, before any agent can read them.
            # In production this runs when a recruiter submits a posting, not at load time.
            if findings := scan_text(f"{job.title}\n{job.company}\n{job.description}"):
                self.quarantined[job.job_id] = [f.rule for f in findings]
                logger.warning("Quarantined %s: %s", job.job_id, self.quarantined[job.job_id])
                continue
            self._jobs[job.job_id] = job

    def search(
        self, keywords: str, location: str | None = None, experience_years: int | None = None, limit: int = 5
    ) -> list[Job]:
        terms = {t for t in keywords.lower().split() if len(t) > 2}

        def score(job: Job) -> int:
            text = f"{job.title} {' '.join(job.skills)} {job.description}".lower()
            return sum(term in text for term in terms)

        candidates = [
            job for job in self._jobs.values()
            if (location is None or location.lower() in (job.location.lower(), job.work_mode))
            and (experience_years is None or job.min_experience_years <= experience_years <= job.max_experience_years)
        ]
        ranked = sorted(candidates, key=score, reverse=True)
        return [job for job in ranked if score(job) > 0][:limit]

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id.strip().upper())

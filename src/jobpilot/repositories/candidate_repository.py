"""Candidate profile storage. JSON seed data for now; a users table later."""
import json
from pathlib import Path
from typing import Protocol

from jobpilot.models import Candidate

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "candidates.json"


class CandidateRepository(Protocol):
    def get(self, candidate_id: str) -> Candidate | None: ...


class InMemoryCandidateRepository:
    def __init__(self, seed_file: Path = SEED_FILE):
        self._candidates = {c["candidate_id"]: Candidate(**c) for c in json.loads(seed_file.read_text())}

    def get(self, candidate_id: str) -> Candidate | None:
        return self._candidates.get(candidate_id)

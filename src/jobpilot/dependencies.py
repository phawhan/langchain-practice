"""Builds shared objects once and hands them out (a tiny dependency container).

Swapping storage later (pgvector, Postgres) means changing only these functions.
"""
from dataclasses import dataclass
from functools import lru_cache

from jobpilot.repositories.application_repository import ApplicationRepository, InMemoryApplicationRepository
from jobpilot.repositories.candidate_repository import CandidateRepository, InMemoryCandidateRepository
from jobpilot.repositories.job_repository import InMemoryJobRepository, JobRepository


@dataclass
class UserContext:
    """Who is using the app. Set by the server from the login session, never by the LLM."""

    candidate_id: str


@lru_cache
def get_job_repository() -> JobRepository:
    return InMemoryJobRepository()


@lru_cache
def get_application_repository() -> ApplicationRepository:
    return InMemoryApplicationRepository()


@lru_cache
def get_candidate_repository() -> CandidateRepository:
    return InMemoryCandidateRepository()

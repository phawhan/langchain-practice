"""Job application storage. In memory for now; a real database table later."""
from datetime import date
from typing import Protocol

from jobpilot.models import Application


class ApplicationRepository(Protocol):
    def create(self, candidate_id: str, job_id: str) -> Application: ...

    def find(self, candidate_id: str, job_id: str) -> Application | None: ...

    def list_for_candidate(self, candidate_id: str) -> list[Application]: ...


class InMemoryApplicationRepository:
    def __init__(self):
        self._applications: list[Application] = []

    def create(self, candidate_id: str, job_id: str) -> Application:
        application = Application(
            application_id=f"APP-{len(self._applications) + 1:04d}",
            candidate_id=candidate_id,
            job_id=job_id,
            applied_on=date.today(),
        )
        self._applications.append(application)
        return application

    def find(self, candidate_id: str, job_id: str) -> Application | None:
        return next((a for a in self._applications if (a.candidate_id, a.job_id) == (candidate_id, job_id)), None)

    def list_for_candidate(self, candidate_id: str) -> list[Application]:
        return [a for a in self._applications if a.candidate_id == candidate_id]

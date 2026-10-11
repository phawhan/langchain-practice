"""Domain models: the core business objects of JobPilot."""
from datetime import date
from typing import Literal

from pydantic import BaseModel


class Job(BaseModel):
    job_id: str
    title: str
    company: str
    location: str  # city name, or "Remote"
    work_mode: Literal["onsite", "hybrid", "remote"]
    min_experience_years: int
    max_experience_years: int
    salary_min_lpa: float  # LPA = lakhs per annum (Indian salary convention)
    salary_max_lpa: float
    skills: list[str]
    description: str
    posted_on: date

    def summary(self) -> dict:
        """Short version for search results, so the LLM reads fewer tokens."""
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "experience": f"{self.min_experience_years}-{self.max_experience_years} yrs",
            "salary": f"{self.salary_min_lpa:g}-{self.salary_max_lpa:g} LPA",
        }


class Candidate(BaseModel):
    candidate_id: str
    full_name: str
    headline: str
    experience_years: int
    skills: list[str]
    preferred_locations: list[str]
    expected_salary_lpa: float
    resume_summary: str


class Application(BaseModel):
    application_id: str
    candidate_id: str
    job_id: str
    status: Literal["applied", "shortlisted", "rejected"] = "applied"
    applied_on: date

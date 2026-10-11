"""Tools the job-search agent can call.

@tool turns a function into an LLM tool: its name, type hints and docstring become the
description the LLM reads to decide WHEN to call it and WHAT arguments to pass.
A `runtime` parameter is hidden from the LLM; it carries the logged-in user's context.
"""
from typing import Any

from langchain.tools import ToolRuntime, tool

from jobpilot.dependencies import UserContext, get_application_repository, get_job_repository


@tool
def search_jobs(keywords: str, location: str | None = None, experience_years: int | None = None) -> list[dict]:
    """Search open jobs.

    keywords: role or skills, e.g. "python backend" or "genai langchain".
    location: a city like "Bengaluru", or "remote". Leave empty for any location.
    experience_years: the candidate's years of experience, to match the job's required range.
    """
    jobs = get_job_repository().search(keywords, location, experience_years)
    if not jobs:
        return [{"message": "No matching jobs. Try fewer keywords or remove the location filter."}]
    return [job.summary() for job in jobs]


@tool
def get_job_details(job_id: str) -> dict:
    """Get the full details of one job (skills, description, salary) by its job_id, e.g. "JOB-1002"."""
    job = get_job_repository().get(job_id)
    if job is None:
        return {"error": f"No job with id '{job_id}'. Use search_jobs to find valid job ids."}
    return job.model_dump(mode="json")


@tool
def apply_to_job(job_id: str, runtime: ToolRuntime[UserContext, Any]) -> dict:
    """Submit the current user's application to a job. Only call this when the user clearly asks to apply."""
    context: UserContext = runtime.context  # from the session, never from the LLM
    candidate_id = context.candidate_id
    if get_job_repository().get(job_id) is None:
        return {"error": f"No job with id '{job_id}'."}
    applications = get_application_repository()
    if existing := applications.find(candidate_id, job_id.upper()):
        return {"message": "Already applied.", **existing.model_dump(mode="json")}
    return {"message": "Application submitted.", **applications.create(candidate_id, job_id.upper()).model_dump(mode="json")}


@tool
def list_my_applications(runtime: ToolRuntime[UserContext, Any]) -> list[dict]:
    """List the jobs the current user has applied to, with their status."""
    applications = get_application_repository().list_for_candidate(runtime.context.candidate_id)
    return [a.model_dump(mode="json") for a in applications] or [{"message": "No applications yet."}]


JOB_TOOLS = [search_jobs, get_job_details, apply_to_job, list_my_applications]

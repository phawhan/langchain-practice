"""Cover letter tool. The agent sees one simple tool; inside it runs the reflection workflow."""
from typing import Any

from langchain.tools import ToolRuntime, tool

from jobpilot.dependencies import UserContext, get_candidate_repository, get_job_repository
from jobpilot.workflows.cover_letter import generate_reviewed_cover_letter


@tool
def write_cover_letter(job_id: str, runtime: ToolRuntime[UserContext, Any]) -> dict:
    """Write an honest, self-reviewed cover letter for the current user for one job_id, e.g. "JOB-1003"."""
    candidate = get_candidate_repository().get(runtime.context.candidate_id)
    job = get_job_repository().get(job_id)
    if candidate is None or job is None:
        return {"error": f"Could not find {'the profile' if candidate is None else f'job {job_id}'}."}
    return generate_reviewed_cover_letter(candidate, job).model_dump()

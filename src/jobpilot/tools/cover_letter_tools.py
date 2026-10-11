"""Cover letter tool. The agent sees one simple tool; inside it runs the reflection workflow."""
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any

from langchain.tools import ToolRuntime, tool

from jobpilot.config import settings
from jobpilot.dependencies import UserContext, get_candidate_repository, get_job_repository
from jobpilot.workflows.cover_letter import generate_reviewed_cover_letter

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cover-letter")


@tool
def write_cover_letter(job_id: str, runtime: ToolRuntime[UserContext, Any]) -> dict:
    """Write an honest, self-reviewed cover letter for the current user for one job_id, e.g. "JOB-1003"."""
    candidate = get_candidate_repository().get(runtime.context.candidate_id)
    job = get_job_repository().get(job_id)
    if candidate is None or job is None:
        return {"error": f"Could not find {'the profile' if candidate is None else f'job {job_id}'}."}
    # Timeout (4.8): the reflection loop makes several LLM calls and once took 6+ minutes.
    # The agent gets a clear message instead of hanging. (The background thread can't be killed,
    # so it finishes on its own; in production this becomes a background job + status tool.)
    future = _executor.submit(generate_reviewed_cover_letter, candidate, job)
    try:
        return future.result(timeout=settings.cover_letter_timeout_seconds).model_dump()
    except FutureTimeoutError:
        return {"error": "Cover letter generation timed out. Tell the user to try again in a few minutes."}

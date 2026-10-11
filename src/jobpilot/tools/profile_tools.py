"""Tools about the logged-in candidate."""
from typing import Any

from langchain.tools import ToolRuntime, tool

from jobpilot.dependencies import UserContext, get_candidate_repository


@tool
def get_my_profile(runtime: ToolRuntime[UserContext, Any]) -> dict:
    """Get the current user's profile: experience, skills, preferred locations, expected salary, resume summary."""
    candidate = get_candidate_repository().get(runtime.context.candidate_id)
    if candidate is None:
        return {"error": "Profile not found. Ask the user to complete their profile."}
    return candidate.model_dump()

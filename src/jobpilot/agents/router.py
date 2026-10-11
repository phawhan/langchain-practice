"""Router pattern: one cheap LLM call classifies the request, then plain code sends it to a specialist.

Each specialist gets a short prompt and only the tools it needs, which makes it more accurate
than one giant agent that does everything.
"""
from typing import Literal

from pydantic import BaseModel, Field

from jobpilot.llm import get_chat_model

Route = Literal["job_search", "career_coach", "off_topic"]

ROUTER_PROMPT = """Classify the user's latest message for a job-search app.
- job_search: finding jobs, job details, applying, or checking applications.
- career_coach: resume or profile feedback, skill gaps, cover letters, interview preparation, career advice.
- off_topic: anything unrelated to jobs or careers.
Use the recent conversation to understand short follow-ups like "apply to it"."""

OFF_TOPIC_REPLY = "I can help with job search, applications, and career advice. What would you like to do?"


class RouteDecision(BaseModel):
    route: Route = Field(description="Which specialist should handle the message")
    reason: str = Field(description="One short sentence explaining the choice")


def classify_intent(recent_messages: list) -> RouteDecision:
    """recent_messages: the last few user/assistant turns, newest last."""
    router_llm = get_chat_model(thinking=False).with_structured_output(RouteDecision)  # typed JSON, fast
    return router_llm.invoke([{"role": "system", "content": ROUTER_PROMPT}, *recent_messages])

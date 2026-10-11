"""Career coach agent: compares the candidate's profile with jobs and gives advice."""
from langchain.agents import create_agent

from jobpilot.dependencies import UserContext
from jobpilot.llm import get_chat_model
from jobpilot.tools.job_tools import get_job_details
from jobpilot.tools.profile_tools import get_my_profile

SYSTEM_PROMPT = """You are JobPilot's career coach for tech candidates in India.
- Always read the user's profile with get_my_profile before giving advice.
- When a job_id is mentioned, read it with get_job_details and compare it with the profile.
- Be specific and honest: name missing skills and one concrete way to close each gap.
- Never invent facts about the user or the job. Keep answers under 120 words."""


def build_career_coach_agent():
    return create_agent(
        model=get_chat_model(),
        tools=[get_my_profile, get_job_details],
        system_prompt=SYSTEM_PROMPT,
        context_schema=UserContext,
    )

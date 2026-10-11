"""Career coach agent: compares the candidate's profile with jobs and gives advice."""
from langchain.agents import create_agent

from jobpilot.agents.middleware import standard_middleware
from jobpilot.dependencies import UserContext
from jobpilot.llm import get_chat_model
from jobpilot.memory.long_term import MEMORY_TOOLS
from jobpilot.memory.stores import get_memory_store
from jobpilot.tools.cover_letter_tools import write_cover_letter
from jobpilot.tools.job_tools import get_job_details
from jobpilot.tools.profile_tools import get_my_profile

SYSTEM_PROMPT = """You are JobPilot's career coach for tech candidates in India.
- Always read the user's profile with get_my_profile before giving advice.
- When a job_id is mentioned, read it with get_job_details and compare it with the profile.
- For a cover letter, call write_cover_letter and return the letter; if approved is false, mention the open issues.
- Be specific and honest: name missing skills and one concrete way to close each gap.
- Never invent facts about the user or the job. Keep answers under 120 words."""


def build_career_coach_agent(include_memory_tools: bool = True):
    """include_memory_tools=False for workers/subagents that read job postings but don't talk to the user."""
    tools = [get_my_profile, get_job_details, write_cover_letter, *(MEMORY_TOOLS if include_memory_tools else [])]
    return create_agent(
        model=get_chat_model(),
        tools=tools,
        middleware=standard_middleware(SYSTEM_PROMPT, tools),
        context_schema=UserContext,
        store=get_memory_store(),
    )

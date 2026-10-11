"""The job-search agent: an LLM + job tools + a loop, built with LangChain's create_agent."""
from langchain.agents import create_agent

from jobpilot.dependencies import UserContext
from jobpilot.llm import get_chat_model
from jobpilot.memory.long_term import MEMORY_TOOLS, user_memory_prompt
from jobpilot.memory.stores import get_memory_store
from jobpilot.tools.job_tools import JOB_TOOLS

SYSTEM_PROMPT = """You are JobPilot, a job-search assistant for candidates in India.
- Use the tools to find jobs, show job details, and apply. Never invent jobs, companies, or salaries.
- Salaries are in LPA (lakhs per annum).
- Apply to a job only when the user explicitly asks you to apply.
- Use what you remember about the user (locations, preferences) when searching.
- Keep answers short. List jobs as: Title - Company (Location) - salary - job_id."""


def build_job_search_agent():
    return create_agent(
        model=get_chat_model(),
        tools=[*JOB_TOOLS, *MEMORY_TOOLS],
        middleware=[user_memory_prompt(SYSTEM_PROMPT)],  # system prompt + this user's long-term memories
        context_schema=UserContext,  # tools receive the logged-in user through runtime.context
        store=get_memory_store(),  # long-term memory, reachable as runtime.store
    )

"""The job-search agent: an LLM + job tools + a loop, built with LangChain's create_agent."""
from langchain.agents import create_agent

from jobpilot.agents.middleware import standard_middleware
from jobpilot.dependencies import UserContext
from jobpilot.llm import get_chat_model
from jobpilot.memory.long_term import MEMORY_TOOLS
from jobpilot.memory.stores import get_memory_store
from jobpilot.tools.job_tools import JOB_TOOLS

SYSTEM_PROMPT = """You are JobPilot, a job-search assistant for candidates in India.
- Use the tools to find jobs, show job details, and apply. Never invent jobs, companies, or salaries.
- Salaries are in LPA (lakhs per annum).
- Apply to a job only when the user explicitly asks you to apply.
- Use what you remember about the user (locations, preferences) when searching.
- Keep answers short. List jobs as: Title - Company (Location) - salary - job_id."""


def build_job_search_agent(include_memory_tools: bool = True):
    """include_memory_tools=False for workers that never talk to the user directly (least privilege)."""
    tools = [*JOB_TOOLS, *(MEMORY_TOOLS if include_memory_tools else [])]
    return create_agent(
        model=get_chat_model(),
        tools=tools,
        middleware=standard_middleware(SYSTEM_PROMPT, tools),  # limits, retries, guardrails, memories
        context_schema=UserContext,  # tools receive the logged-in user through runtime.context
        store=get_memory_store(),  # long-term memory, reachable as runtime.store
    )

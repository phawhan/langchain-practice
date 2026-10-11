"""Supervisor pattern: a ReAct agent whose tools are other agents (workers).

The supervisor decides which worker to call, reads the worker's answer, and decides the next
step - so it can chain workers in sequence ("find a job, THEN check my skill gaps for it").
Each worker runs in a fresh, separate conversation, so its tool output never fills the
supervisor's memory; only the worker's final answer comes back.
"""
from functools import lru_cache
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import ToolRuntime, tool

from jobpilot.agents.career_coach_agent import build_career_coach_agent
from jobpilot.agents.job_search_agent import build_job_search_agent
from jobpilot.agents.middleware import standard_middleware
from jobpilot.config import settings
from jobpilot.dependencies import UserContext
from jobpilot.llm import get_chat_model
from jobpilot.memory.long_term import MEMORY_TOOLS
from jobpilot.memory.stores import get_checkpointer, get_memory_store

SUPERVISOR_PROMPT = """You are JobPilot's supervisor. You never search or give advice yourself; you delegate.
- ask_job_search_specialist: finding jobs, job details, applying, application status.
- ask_career_coach: profile feedback, skill gaps, cover letters, interview preparation.
If a request needs both, call them one after another and pass on what you learned
(for example, give the career coach the job_id that the job search specialist found).
Give each specialist a complete, self-contained task: it cannot see this conversation,
so include relevant remembered preferences (e.g. preferred locations) in the task.
When the user states a lasting preference or fact, save it with remember_fact.
Finish with one short combined answer for the user."""


# Workers never see the user's messages, only the supervisor's task text, so they get no memory
# tools: only the supervisor (which hears the user directly) may save memories. Least privilege.
@lru_cache
def _job_search_worker():
    return build_job_search_agent(include_memory_tools=False)


@lru_cache
def _career_coach_worker():
    return build_career_coach_agent(include_memory_tools=False)


def _run_worker(worker, task: str, context: UserContext) -> str:
    """Run a worker on a fresh conversation and return only its final answer."""
    result = worker.invoke(
        {"messages": [{"role": "user", "content": task}]},
        config={"recursion_limit": settings.max_agent_steps},
        context=context,  # the logged-in user flows down to the worker's tools
    )
    return result["messages"][-1].content


@tool
def ask_job_search_specialist(task: str, runtime: ToolRuntime[UserContext, Any]) -> str:
    """Delegate a job-search task: find jobs, get job details, apply, or list applications.

    task: a complete instruction, e.g. "Find remote GenAI jobs for 3 years of experience".
    """
    return _run_worker(_job_search_worker(), task, runtime.context)


@tool
def ask_career_coach(task: str, runtime: ToolRuntime[UserContext, Any]) -> str:
    """Delegate a career task: profile feedback, skill gaps for a job_id, cover letters, interview prep.

    task: a complete instruction, e.g. "Which skills am I missing for JOB-1003?".
    """
    return _run_worker(_career_coach_worker(), task, runtime.context)


def build_supervisor_agent():
    """The supervisor owns the conversation, so it carries all three kinds of memory."""
    tools = [ask_job_search_specialist, ask_career_coach, *MEMORY_TOOLS]
    return create_agent(
        model=get_chat_model(),
        tools=tools,
        middleware=[
            # SHORT-TERM, long chats: past 30 messages, older ones become one summary; last 10 kept word for word
            SummarizationMiddleware(model=get_chat_model(), trigger=("messages", 30), keep=("messages", 10)),
            # limits, retries, fallback, PII masking, memory-aware prompt (LONG-TERM), output guardrail
            *standard_middleware(SUPERVISOR_PROMPT, tools),
        ],
        context_schema=UserContext,
        checkpointer=get_checkpointer(),  # SHORT-TERM, persisted: the conversation is saved per thread_id
        store=get_memory_store(),  # LONG-TERM store, shared with the workers' tools
    )

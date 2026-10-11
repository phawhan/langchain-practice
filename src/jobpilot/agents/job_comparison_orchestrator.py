"""Orchestrator-subagents pattern: split a task into independent pieces, run subagents in parallel, combine.

Use case: "Compare JOB-1002, JOB-1003 and JOB-1010 for me."
  1. SPLIT    - one LLM call turns the request into subtasks (a plan our code holds as data)
  2. FAN OUT  - one subagent per job, all running at the same time, each with a fresh small context
  3. COMBINE  - a synthesizer merges the short results into one answer

Differs from the supervisor: the pieces don't depend on each other, so they run side by side
instead of one after another, and the orchestrator only ever reads short summaries.
"""
import asyncio

from pydantic import BaseModel, Field

from jobpilot.agents.career_coach_agent import build_career_coach_agent
from jobpilot.config import settings
from jobpilot.dependencies import UserContext
from jobpilot.llm import get_chat_model

MAX_PARALLEL_SUBAGENTS = 3  # cap concurrency: API rate limits, or CPU when the LLM runs locally

PLANNER_PROMPT = """Split the user's request into independent subtasks, exactly one per job_id mentioned.
Each instruction must be self-contained, for example:
"Assess how well my profile fits JOB-1003: matching skills, missing skills, salary vs my expectation. Reply in 3 short lines."
Return no subtasks if the request mentions no job ids."""

SYNTHESIZER_PROMPT = """You combine analyses of several jobs into one answer for the candidate.
Use only the analyses given. Write one line per job, then a one-sentence recommendation.
If an analysis failed, say so for that job instead of guessing."""


class Subtask(BaseModel):
    job_id: str = Field(description="One job id, e.g. JOB-1003")
    instruction: str = Field(description="Self-contained instruction for the subagent about this job")


class OrchestrationPlan(BaseModel):
    subtasks: list[Subtask]


async def _run_subagent(subagent, subtask: Subtask, context: UserContext, limit: asyncio.Semaphore) -> str:
    async with limit:  # waits here if MAX_PARALLEL_SUBAGENTS are already running
        result = await subagent.ainvoke(
            {"messages": [{"role": "user", "content": subtask.instruction}]},
            config={"recursion_limit": settings.max_agent_steps},
            context=context,
        )
        return result["messages"][-1].content


async def compare_jobs(request: str, context: UserContext) -> str:
    # 1. SPLIT
    planner = get_chat_model(thinking=False).with_structured_output(OrchestrationPlan)
    plan = await planner.ainvoke([("system", PLANNER_PROMPT), ("user", request)])
    if not plan.subtasks:
        return "Please mention the job ids you want to compare, e.g. JOB-1002 and JOB-1003."

    # 2. FAN OUT
    # subagents read third-party job postings, so they get no memory tools (least privilege);
    # one compiled agent can safely serve many parallel runs
    subagent = build_career_coach_agent(include_memory_tools=False)
    limit = asyncio.Semaphore(MAX_PARALLEL_SUBAGENTS)
    results = await asyncio.gather(
        *(_run_subagent(subagent, subtask, context, limit) for subtask in plan.subtasks),
        return_exceptions=True,  # one failed subagent must not sink the others (partial results)
    )

    # 3. COMBINE
    analyses = "\n\n".join(
        f"{subtask.job_id}: {'ANALYSIS FAILED' if isinstance(result, Exception) else result}"
        for subtask, result in zip(plan.subtasks, results)
    )
    synthesizer = get_chat_model()
    answer = await synthesizer.ainvoke([("system", SYNTHESIZER_PROMPT), ("user", f"Request: {request}\n\n{analyses}")])
    return answer.content

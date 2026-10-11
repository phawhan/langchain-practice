"""The safety stack every JobPilot agent gets: reliability (4.8) + security (4.9) + memory (4.5).

Middleware wraps each model and tool call, so these rules hold no matter what the LLM decides.
List order = outermost first.
"""
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)

from jobpilot.config import settings
from jobpilot.llm import get_fallback_chat_model
from jobpilot.memory.long_term import user_memory_prompt
from jobpilot.security.guardrails import SECURITY_RULES, block_unsafe_answers, pii_middleware

# Only tools that are safe to repeat get automatic retries (apply_to_job is idempotent, but a
# write action should fail visibly rather than be retried silently).
READ_ONLY_TOOLS = {"search_jobs", "get_job_details", "get_my_profile", "list_my_applications"}


def reliability_middleware(tools: list) -> list:
    stack = [
        # loop limits: stop runaway agents and cap cost per request and per conversation
        ModelCallLimitMiddleware(
            run_limit=settings.max_model_calls_per_request,
            thread_limit=settings.max_model_calls_per_thread,
            exit_behavior="end",  # finish gracefully instead of raising
        ),
        ToolCallLimitMiddleware(tool_name="search_jobs", run_limit=settings.max_searches_per_request),
        # retries: transient model errors (timeouts, rate limits), exponential backoff + jitter
        ModelRetryMiddleware(max_retries=2, backoff_factor=2.0, initial_delay=1.0, jitter=True),
    ]
    retryable = [t.name for t in tools if t.name in READ_ONLY_TOOLS]
    if retryable:
        stack.append(ToolRetryMiddleware(max_retries=2, tools=retryable))
    if fallback := get_fallback_chat_model():  # plan B model, only if configured
        stack.append(ModelFallbackMiddleware(fallback))
    return stack


def standard_middleware(base_prompt: str, tools: list) -> list:
    """Full stack for an agent: limits, retries, fallback, PII masking, memory-aware prompt, output check."""
    return [
        *reliability_middleware(tools),
        *pii_middleware(),
        user_memory_prompt(f"{base_prompt}\n\n{SECURITY_RULES}"),
        block_unsafe_answers,
    ]

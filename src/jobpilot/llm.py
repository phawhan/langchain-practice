"""The one place that creates chat models. Switch to Claude or Bedrock by changing only this file."""
from langchain_ollama import ChatOllama

from jobpilot.config import settings


def get_chat_model(temperature: float = 0.0, thinking: bool = True, model: str | None = None) -> ChatOllama:
    """temperature: 0 = predictable facts, higher = more creative writing.

    thinking: qwen3 "thinks" before answering. With thinking=True that thinking goes into
    additional_kwargs["reasoning_content"] instead of leaking into the reply text.
    Use thinking=False for structured output (router, critic): the JSON schema already constrains
    the reply, and skipping thinking took a critic call from 5+ minutes to 4 seconds.
    """
    return ChatOllama(
        model=model or settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
        reasoning=thinking,
        client_kwargs={"timeout": settings.llm_timeout_seconds},  # never wait forever on one model call
    )


def get_fallback_chat_model() -> ChatOllama | None:
    """Backup model used when the main one keeps failing. None if no fallback is configured."""
    if not settings.fallback_llm_model:
        return None
    return get_chat_model(model=settings.fallback_llm_model)

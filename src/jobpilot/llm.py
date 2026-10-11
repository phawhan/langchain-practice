"""The one place that creates the chat model. Switch to Claude or Bedrock by changing only this file."""
from langchain_ollama import ChatOllama

from jobpilot.config import settings


def get_chat_model(temperature: float = 0.0, thinking: bool = True) -> ChatOllama:
    """temperature: 0 = predictable facts, higher = more creative writing.

    thinking: qwen3 "thinks" before answering. With thinking=True that thinking goes into
    additional_kwargs["reasoning_content"] instead of leaking into the reply text.
    Use thinking=False for structured output (router, critic): the JSON schema already constrains
    the reply, and skipping thinking took a critic call from 5+ minutes to 4 seconds.
    """
    return ChatOllama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
        reasoning=thinking,
    )

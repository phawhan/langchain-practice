"""App settings, read from environment variables with local-dev defaults."""
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    llm_model: str = field(default_factory=lambda: os.getenv("JOBPILOT_LLM_MODEL", "qwen3:4b"))
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    max_agent_steps: int = field(default_factory=lambda: int(os.getenv("JOBPILOT_MAX_AGENT_STEPS", "12")))
    # SQLite file for conversation checkpoints + long-term memories (Postgres in production)
    memory_db_path: str = field(default_factory=lambda: os.getenv("JOBPILOT_MEMORY_DB", ".jobpilot/memory.sqlite"))

    # --- Reliability (4.8) ---
    llm_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("JOBPILOT_LLM_TIMEOUT", "180")))
    fallback_llm_model: str | None = field(default_factory=lambda: os.getenv("JOBPILOT_FALLBACK_LLM_MODEL") or None)
    max_model_calls_per_request: int = field(default_factory=lambda: int(os.getenv("JOBPILOT_MAX_MODEL_CALLS", "8")))
    max_model_calls_per_thread: int = field(default_factory=lambda: int(os.getenv("JOBPILOT_MAX_THREAD_CALLS", "200")))
    max_searches_per_request: int = field(default_factory=lambda: int(os.getenv("JOBPILOT_MAX_SEARCHES", "3")))
    cover_letter_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("JOBPILOT_COVER_LETTER_TIMEOUT", "300")))

    # --- Security (4.9) ---
    max_input_chars: int = field(default_factory=lambda: int(os.getenv("JOBPILOT_MAX_INPUT_CHARS", "2000")))


settings = Settings()

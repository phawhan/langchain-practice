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


settings = Settings()

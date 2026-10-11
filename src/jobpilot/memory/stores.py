"""Where memory lives on disk.

- Checkpointer = SHORT-TERM memory: saves each conversation's full state after every step,
  keyed by thread_id, so a chat survives restarts and can pause/resume (needed for 4.7).
- Store = LONG-TERM memory: facts about a user that outlive any single conversation.

SQLite keeps local dev simple. In production both swap to Postgres (PostgresSaver, PostgresStore).
"""
import sqlite3
from functools import lru_cache
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore

from jobpilot.config import settings


@lru_cache
def _connection() -> sqlite3.Connection:
    Path(settings.memory_db_path).parent.mkdir(parents=True, exist_ok=True)
    # isolation_level=None (autocommit): the store and saver manage their own transactions
    return sqlite3.connect(settings.memory_db_path, check_same_thread=False, isolation_level=None)


@lru_cache
def get_checkpointer() -> SqliteSaver:
    return SqliteSaver(_connection())


@lru_cache
def get_memory_store() -> SqliteStore:
    store = SqliteStore(_connection())
    store.setup()  # creates tables on first run
    return store

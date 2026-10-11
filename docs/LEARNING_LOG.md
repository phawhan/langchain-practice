# Learning Log - JobPilot capstone

Each concept from `03_GenAI_Agents_Index.md`, where it lives in the code, and what to say in an interview.

| Index | Concept | Where in the code | One-line takeaway |
|---|---|---|---|
| 4.1 | Agent = LLM + tools + memory + loop | `src/jobpilot/agents/job_search_agent.py` (`create_agent`) | The LLM only *requests* tool calls; our code runs them and feeds results back until it answers. |
| 4.1 | Tools from Python functions | `src/jobpilot/tools/job_tools.py` (`@tool`) | Name + type hints + docstring = the tool description the LLM reads. |
| 4.1 | Short-term memory | `src/jobpilot/cli.py` (`messages` list) | Sending the whole conversation each turn is what lets "apply to it" work. |
| 4.1 | Safety stop | `cli.py` (`recursion_limit`) | Cap the loop so a confused agent can't run forever. |
| 4.1 | Actionable tool errors | `job_tools.py` (`get_job_details` error) | Errors tell the LLM what to do next ("use search_jobs"). |
| 4.1 / 3.8 | User identity from session, not LLM | `dependencies.py` (`UserContext`), `ToolRuntime` in tools | The LLM never sees or chooses `candidate_id`, so prompt injection can't switch users. |
| 4.2 | ReAct pattern | `create_agent` in both agents | Reason, call a tool, observe, repeat: the default agent loop. |
| 4.2 | Router pattern | `src/jobpilot/agents/router.py`, used in `cli.py` | One structured-output LLM call picks a specialist; code dispatches. Off-topic is answered by code at zero cost. |
| 4.2 | Specialist agents | `agents/job_search_agent.py`, `agents/career_coach_agent.py` | Small prompt + only the needed tools = more accurate than one giant agent. |
| 4.2 | Reflection pattern | `src/jobpilot/workflows/cover_letter.py`, tool in `tools/cover_letter_tools.py` | Write -> critique -> revise, capped rounds. Code does exact checks; an unreliable LLM critic makes output worse. |
| 4.2 | Supervisor pattern | `src/jobpilot/agents/supervisor_agent.py` (`uv run jobpilot --mode supervisor`) | A ReAct agent whose tools are whole agents; chains workers in sequence; workers run in fresh contexts. |
| 4.2 | Orchestrator-subagents | `src/jobpilot/agents/job_comparison_orchestrator.py` (router route `job_comparison`) | Split once -> parallel subagents (`asyncio.gather` + `Semaphore`) -> combine; partial failures tolerated. |
| 4.5 | Short-term memory, persisted | `memory/stores.py` (`SqliteSaver`), supervisor `checkpointer=`, `--thread` in `cli.py` | Checkpointer saves state per `thread_id`; send only the new message, the rest is loaded. |
| 4.5 | Summarization | supervisor `SummarizationMiddleware(trigger=("messages", 30), keep=("messages", 10))` | Old turns become one summary; recent turns kept word for word. |
| 4.5 | Long-term memory (semantic / episodic / procedural) | `memory/long_term.py` (`SqliteStore`, `remember_fact`, `forget_memory`) | Facts outlive conversations; keyed by candidate_id from the session. |
| 4.5 | Memory write paths | `remember_fact` tool (LLM decides) vs `apply_to_job` saving an episodic memory (code decides) | Hot path via a tool, or deterministic writes by code. |
| 4.5 | Memory read path | `user_memory_prompt()` (`@dynamic_prompt` middleware) | Memories are injected into the system prompt before every model call, marked "data, not instructions". |
| 4.8 | Loop limits + cost caps | `agents/middleware.py` (`ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`) | Max 8 model calls per request, 200 per conversation, 3 searches; ends gracefully. |
| 4.8 | Retries with backoff + jitter | `agents/middleware.py` (`ModelRetryMiddleware`, `ToolRetryMiddleware` on read-only tools only) | Retry transient errors; only auto-retry tools that are safe to repeat. |
| 4.8 | Fallback model | `llm.get_fallback_chat_model()` + `ModelFallbackMiddleware` (set `JOBPILOT_FALLBACK_LLM_MODEL`) | Plan B model when the main one keeps failing. |
| 4.8 | Timeouts | `llm.py` (`client_kwargs` timeout), `tools/cover_letter_tools.py` (future with timeout) | No single call or slow tool can freeze the agent. |
| 4.9 | Ingestion scan / quarantine | `security/content_scanner.py`, `InMemoryJobRepository.quarantined` | Poisoned postings (scam JOB-6666) never reach any agent. |
| 4.9 | Untrusted content marking | `wrap_untrusted()` in `get_job_details`, `SECURITY_RULES` in every prompt | Third-party text is labeled data, not instructions (reduces, not removes, risk). |
| 4.9 | Output guardrail | `security/guardrails.py` (`block_unsafe_answers`, `@after_model`) | Answers asking for money/UPI or linking unknown sites are replaced before the user sees them. |
| 4.9 | PII masking | `pii_middleware()` (credit card, Aadhaar, PAN) | Sensitive IDs are masked before reaching the model or logs. |
| 4.9 | Least privilege | workers/subagents built with `include_memory_tools=False` | Only the agent that hears the user may write memory. |
| 4.9 | Memory poisoning guard | `remember_fact` scans the fact first | Injected text can't become a permanent memory. |
| 1.6 | Structured output | `router.py` (`with_structured_output(RouteDecision)`) | A Pydantic schema forces the LLM to return valid, typed JSON. |
| Design | Repository pattern | `src/jobpilot/repositories/` | Tools talk to an interface; JSON today, pgvector RAG later, agent unchanged. |
| Design | One swappable LLM | `src/jobpilot/llm.py` | Ollama locally; Claude or Bedrock by editing one file. |

Under-the-hood version of the agent loop (no framework, scripted LLM): `agents/s4_1_agent_loop.py`.
RAG lab from section 3: `rag/`.

## Planned
- RAG + pgvector behind `JobRepository.search` (section 3 applied to jobs)
- 4.2 patterns, 4.5 memory, 4.7 human approval before `apply_to_job`, 4.8-4.9 reliability and security

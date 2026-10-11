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
| 1.6 | Structured output | `router.py` (`with_structured_output(RouteDecision)`) | A Pydantic schema forces the LLM to return valid, typed JSON. |
| Design | Repository pattern | `src/jobpilot/repositories/` | Tools talk to an interface; JSON today, pgvector RAG later, agent unchanged. |
| Design | One swappable LLM | `src/jobpilot/llm.py` | Ollama locally; Claude or Bedrock by editing one file. |

Under-the-hood version of the agent loop (no framework, scripted LLM): `agents/s4_1_agent_loop.py`.
RAG lab from section 3: `rag/`.

## Planned
- RAG + pgvector behind `JobRepository.search` (section 3 applied to jobs)
- 4.2 patterns, 4.5 memory, 4.7 human approval before `apply_to_job`, 4.8-4.9 reliability and security

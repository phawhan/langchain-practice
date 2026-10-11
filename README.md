# JobPilot

AI job-search assistant (Naukri-style). GenAI capstone project: every concept learned is built into this app.
Concept-to-code map: [docs/LEARNING_LOG.md](docs/LEARNING_LOG.md).

## Setup
```
brew install ollama && ollama serve     # local LLM runner (keep it running)
ollama pull qwen3:4b                    # ~2.5 GB model
uv sync --inexact                       # install the project (--inexact keeps the rag/ lab packages)
```

## Run
```
uv run jobpilot          # chat in the terminal; tool calls are printed so you can watch the agent
uv run pytest            # tests (no LLM needed)
```

## Structure
```
src/jobpilot/
  agents/job_search_agent.py   the agent (LLM + tools + loop)
  tools/job_tools.py           search_jobs, get_job_details, apply_to_job, list_my_applications
  repositories/                data access (in-memory now, pgvector later)
  data/jobs.json               seed job postings
  models.py                    Job, Application
  dependencies.py              UserContext + shared repositories
  llm.py                       chat model (swap provider here)
  config.py                    settings from environment variables
  cli.py                       terminal chat entry point
tests/                         unit tests
docs/                          interview index + learning log
rag/                           section 3 RAG lab (standalone scripts)
```

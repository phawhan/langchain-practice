# 03 — GenAI & AI Agents Interview Index
Covers: Job 2 (Senior AI Engineer) + the GenAI parts of Job 1
Legend: ⭐ likely | ⚠️ gap vs JD | 🎯 your resume hook

---

## 1. LLM Fundamentals ⭐
1.1 Transformers, attention, tokens, context window, embeddings
1.2 Sampling: temperature, top-p, top-k, max tokens, stop sequences
1.3 Hallucination: causes and mitigation
1.4 Model families and tradeoffs: GPT-4, Gemini, Claude, Llama/open-source, small vs large
1.5 Cost/latency optimization: caching, prompt compression, model routing, batching, streaming
1.6 Function/tool calling and structured outputs (JSON mode, schema-constrained) 🎯

## 2. Prompt Engineering ⭐
2.1 System vs user prompts, few-shot, chain-of-thought, ReAct, self-consistency
2.2 Structured output + validation + retry loops 🎯 (Divami-AURA, IIRM)
2.3 Guardrails: input/output filters, PII redaction, topic restriction, prompt-injection defense
2.4 Prompt versioning, templates, A/B testing
2.5 Prompts for consistency across variable input quality 🎯

## 3. RAG ⭐
3.1 Pipeline: ingest → chunk → embed → store → retrieve → rerank → generate
3.2 Chunking strategies (fixed, recursive, semantic, structure-aware)
3.3 Embedding models, dimensionality, similarity metrics (cosine, dot, L2)
3.4 Vector DBs: pgvector 🎯, Pinecone 🎯; others: OpenSearch, Qdrant, Weaviate, Chroma ⚠️
3.5 Index types: HNSW vs IVF, recall/latency tradeoff
3.6 Hybrid search (BM25 + vector), metadata filtering, re-ranking
3.7 Advanced RAG: query rewriting, HyDE, multi-query, parent-child retrieval, agentic RAG, GraphRAG
3.8 Multi-tenant RAG isolation 🎯 ARKA
3.9 Evaluation: faithfulness, context precision/recall, answer relevance (RAGAS)
3.10 Failure modes: bad chunks, stale data, lost-in-the-middle
3.11 🎯 ConnectIQ policy-KB RAG; IIRM policy configuration; ARKA doc ingestion

## 4. Agentic AI ⭐ (Job 2 core)
4.1 Agent = LLM + tools + memory + planning + control loop
4.2 Patterns: ReAct, plan-and-execute, reflection, router, supervisor/worker, orchestrator-subagents
4.3 Workflows vs agents — when NOT to use an agent
4.4 Tool design: clear schemas, idempotency, error messages the model can act on, timeouts
4.5 **Memory**: short-term (conversation/state), long-term (vector/DB), summarization, episodic vs semantic; DynamoDB/Redis/pgvector as stores
4.6 Reasoning pipelines: decomposition, verification, self-correction
4.7 Human-in-the-loop and escalation 🎯 (ConnectIQ live-agent fallback)
4.8 Reliability: loop limits, retries, fallbacks, deterministic guardrails, cost caps
4.9 Security: tool permission scoping, prompt injection through tool outputs

## 5. Frameworks ⭐
5.1 LangChain: chains, runnables (LCEL), retrievers, output parsers 🎯
5.2 LangGraph: state, nodes, edges, conditional routing, checkpointers, interrupts, streaming 🎯
5.3 Pydantic AI: agents, typed tools, dependencies, result validation 🎯
5.4 Compare LangGraph vs Pydantic AI vs CrewAI vs AutoGen vs OpenAI Agents SDK vs Strands ⚠️ (AWS-native Strands is worth reading)
5.5 When to skip frameworks and write the loop yourself

## 6. Multi-Agent Systems ⭐
6.1 Topologies: supervisor, hierarchical, peer-to-peer, pipeline, blackboard
6.2 🎯 ARKA deep dive: data-source agents + planner + synthesizer
   - How the plan is represented (typed schema)
   - How agents run in parallel; how failures and partial results are handled
   - How you stop wrong answers (grounding/citations)
   - How tenant isolation is enforced at the agent/tool level
6.3 Shared state vs message passing; context handoff and context-window budgeting
6.4 Debugging and evaluating multi-agent traces

## 7. A2A (Agent-to-Agent) ⚠️ (Job 2 explicit)
7.1 What A2A is: open protocol for agents from different vendors/frameworks to discover and talk to each other
7.2 Core concepts: Agent Card (capability discovery), tasks and task lifecycle, messages/artifacts, streaming, auth
7.3 A2A vs MCP: A2A = agent↔agent collaboration; MCP = agent↔tools/data
7.4 Your honest bridge: ARKA planner↔data-source agents is the same idea in-process; explain how you'd expose them over A2A (HTTP + agent card)
7.5 Prep action: read the A2A spec and run one sample client/server

## 8. MCP — Model Context Protocol ⚠️ (Job 2 explicit)
8.1 Architecture: host, client, server; transports (stdio, streamable HTTP)
8.2 Primitives: tools, resources, prompts; sampling; roots
8.3 Building an MCP server in Python (FastMCP / official SDK) — expose a DB query tool and a docs resource
8.4 Auth (OAuth), security, tool-permission and prompt-injection risks
8.5 MCP vs plain function calling vs OpenAPI tools
8.6 Your bridge: wrap your Salesforce/JIRA/Google data-source tools from ARKA as MCP servers
8.7 Prep action: build and demo a small MCP server this week

## 9. Fine-Tuning & Model Adaptation ⚠️ (Job 2: "fine-tune LLMs")
9.1 Prompting vs RAG vs fine-tuning: decision framework
9.2 SFT, LoRA/QLoRA/PEFT, preference tuning (DPO/RLHF) basics, distillation
9.3 Dataset creation, quality, eval before/after
9.4 Tools: Hugging Face Transformers/PEFT, Bedrock custom model import/fine-tuning, SageMaker
9.5 Be honest: "I've focused on prompt/RAG/agent layers; here's how I'd decide to fine-tune and run it."
9.6 Prep action: run one small LoRA fine-tune (Colab) for a story

## 10. AWS for GenAI ⚠️
10.1 **Amazon Bedrock**: model catalog (Claude, Llama, Nova, Titan), Converse API, Knowledge Bases, Agents for Bedrock, Guardrails, AgentCore, model evaluation
10.2 Deploying agents: Lambda vs ECS/Fargate; API Gateway streaming limits; S3 for docs; secrets and IAM
10.3 Mapping: Gemini/GPT-4 usage → Bedrock equivalents; Azure Document Intelligence → Textract
10.4 Prep action: call Bedrock from boto3 with tool use; deploy one agent endpoint on Fargate

## 11. Evaluation, Observability, MLOps ⭐
11.1 Offline evals: golden datasets, LLM-as-judge, rubric scoring, regression suites in CI
11.2 Online: user feedback, tracing, cost/latency/error dashboards
11.3 Tools: LangSmith 🎯, Logfire 🎯; also Langfuse, Arize Phoenix, Bedrock evaluation ⚠️
11.4 MLOps basics: model/prompt registry, versioning, canary rollout, drift monitoring, rollback
11.5 CI/CD for AI: prompt change → eval gate → deploy
11.6 Testing non-deterministic systems

## 12. Applied Solutions From Your Resume ⭐
- 12.1 **NL2SQL (IIRM)**: schema injection, few-shot, SQL validation, read-only role, query allow-list, error-repair loop, accuracy measurement
- 12.2 **Document intelligence (IIRM)**: ADI/OCR, PAN/Aadhaar extraction, validation, confidence thresholds, PII safety
- 12.3 **Voice AI (ConnectIQ)**: Connect → Lambda → LangGraph; latency budget; Transcribe/Polly; escalation node; DTMF replacement
- 12.4 **Spec generator (Divami-AURA)**: structured outputs, parsing, PDF generation
- 12.5 **Research automation**: Perplexity API pipeline and result verification
- 12.6 **Multi-modal AI** from R&D (Jan–Mar 2025)
- For each: Problem → Architecture → Your role → Hard problem → Metric/outcome → What you'd change

## 13. Emerging Trends & Contributions ⚠️ (Job 2 eligibility)
13.1 Reasoning models, long context vs RAG, computer-use agents, agent protocols (MCP/A2A), small models
13.2 Open-source/blogs/publications: you have none listed → prep action: publish one technical blog (e.g., "Building a multi-agent planner/synthesizer with Pydantic AI") and/or a small OSS MCP server
13.3 Be ready: "What have you read or tried recently?"

## 14. Likely Questions
- Walk through ARKA's architecture end-to-end.
- How do you stop an agent from looping or calling the wrong tool?
- RAG vs fine-tuning for a company-specific knowledge task?
- How do you evaluate an agent in production?
- What is MCP, and how does it differ from A2A?
- How would you secure NL2SQL against destructive or cross-tenant queries?
- How would you move ARKA from Gemini to Bedrock?
- How do you handle memory across long conversations?

## 15. Live-Coding Drills (Python for GenAI) ⭐
Each drill: ≤50 LOC, no framework, explain tradeoffs while coding.
15.1 Cosine similarity + top-k search in numpy (vectorized, no loops)
15.2 Recursive text chunker with size limit and overlap
15.3 Minimal RAG: chunk → embed → retrieve → prompt with citations
15.4 Tool-calling loop from scratch: model → tool call → execute → feed back → stop condition + max-steps cap
15.5 Parallel LLM calls: `asyncio.gather` + `Semaphore` for rate limiting
15.6 Retry with exponential backoff + jitter (decorator form)
15.7 Structured output: Pydantic schema → validate → repair loop on failure
15.8 Streaming responses: iterate chunks, assemble text, handle partial tool calls
15.9 Token budgeting: count tokens, trim conversation history to fit context

---

## Suggested 2-Week Plan
**Days 1–3** Python + FastAPI refresh, Django DRF mini-project
**Days 4–6** AWS core (Lambda, API GW, ECS/Fargate, IAM, DynamoDB, RDS) with hands-on deploy
**Days 7–9** MCP server + A2A sample + Bedrock call
**Days 10–11** Rehearse project stories (ARKA, ConnectIQ, IIRM)
**Days 12–14** Mock interviews, system design, gap-closing answers

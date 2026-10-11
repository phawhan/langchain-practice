# 01 — Python Interview Index
Covers: Job 1 (FastAPI/Django, Python on AWS) + Job 2 (production-ready Python)
Legend: ⭐ = very likely asked | ⚠️ = gap vs JD, prepare extra | 🎯 = your resume hook

---

## 1. Core Language ⭐
1.1 Data types: mutable vs immutable, list/tuple/set/dict internals, hashing
1.2 Dict ordering, `defaultdict`, `Counter`, `deque`, `heapq`, `collections.abc`
1.3 Shallow vs deep copy; pass-by-object-reference
1.4 `is` vs `==`, interning, truthiness
1.5 Mutable default argument trap
1.6 `*args`, `**kwargs`, keyword-only and positional-only params
1.7 Comprehensions, generator expressions, walrus operator
1.8 Exceptions: custom exceptions, `try/except/else/finally`, exception chaining (`raise from`)
1.9 Context managers (`with`, `__enter__/__exit__`, `contextlib`)
1.10 Modules, packages, `__init__.py`, circular imports, `if __name__ == "__main__"`

## 2. Intermediate / Advanced ⭐
2.1 Iterators vs generators vs iterables; `yield`, `yield from`; lazy streaming of LLM output
2.2 Decorators (with arguments, `functools.wraps`, class decorators) — write a retry / timing / cache decorator
2.3 Closures, scope (LEGB), `nonlocal`
2.4 Dunder methods, `__slots__`, `@property`, descriptors
2.5 `dataclasses` vs `NamedTuple` vs Pydantic models
2.6 Type hints: `typing`, `Protocol`, `TypedDict`, `Generic`, `Literal`, `Optional`, mypy
2.7 Metaclasses (basic awareness)
2.8 Memory management: reference counting, garbage collector, memory leaks, `weakref`
2.9 `functools`: `lru_cache`, `partial`, `singledispatch`; `itertools`

## 3. OOP & Design ⭐
3.1 Inheritance, MRO, `super()`, multiple inheritance, mixins
3.2 Abstract classes (`abc`), interfaces via Protocol
3.3 SOLID principles with Python examples
3.4 Design patterns used in backend: Factory, Singleton, Strategy, Repository, Dependency Injection, Adapter
3.5 🎯 Repository / service layer in your NestJS → FastAPI work

## 4. Concurrency & Performance ⭐
4.1 GIL: what it is, what it affects, how to work around it
4.2 Threading vs multiprocessing vs asyncio — when to use which
4.3 `asyncio`: event loop, coroutines, tasks, `gather`, `create_task`, semaphores, timeouts, cancellation
4.4 Blocking calls inside async code (and `run_in_executor`)
4.5 Async DB drivers, `httpx` / `aiohttp`
4.6 Profiling: `cProfile`, `timeit`, `memory_profiler`
4.7 🎯 Parallel tool calls / data-source agents in ARKA; concurrent LLM calls with rate limits

## 5. FastAPI ⭐ (Job 1 core)
5.1 Request lifecycle, ASGI vs WSGI, Uvicorn/Gunicorn workers
5.2 Path/query/body params, validation with Pydantic
5.3 Dependency injection (`Depends`), scopes, reuse for auth and DB sessions
5.4 Async vs sync endpoints — what happens in each
5.5 Middleware, CORS, exception handlers, lifespan events
5.6 Background tasks vs Celery/queue
5.7 Auth: OAuth2 password flow, JWT, API keys
5.8 Streaming responses, SSE, WebSockets (LLM token streaming)
5.9 Testing with `TestClient`, dependency overrides
5.10 OpenAPI/Swagger customization
5.11 🎯 FastAPI in ARKA, IIRM, Divami-AURA

## 6. Django ⚠️ (listed in Job 1, not on your resume)
6.1 MTV architecture, request lifecycle, settings, apps
6.2 ORM: models, migrations, `select_related` vs `prefetch_related`, N+1, `F`/`Q` objects
6.3 Django REST Framework: serializers, viewsets, routers, permissions, throttling
6.4 Middleware, signals, admin
6.5 FastAPI vs Django: honest comparison and when you'd choose each
6.6 Prep action: build a small DRF CRUD API with JWT in 1–2 days

## 7. Pydantic ⭐
7.1 v2 models, validators (`field_validator`, `model_validator`), `Field` constraints
7.2 Serialization, `model_dump`, aliases, settings management (`pydantic-settings`)
7.3 Structured LLM output with Pydantic
7.4 🎯 Validation logic in IIRM and structured output in Divami-AURA

## 8. Databases from Python
8.1 SQLAlchemy (sync + async), sessions, relationships, Alembic migrations
8.2 Connection pooling, transactions, isolation
8.3 `psycopg` / `asyncpg`, raw SQL vs ORM tradeoffs
8.4 `boto3` for DynamoDB/S3/Lambda; pagination, retries, error handling
8.5 ⚠️ You used TypeORM (TypeScript); be ready to explain the SQLAlchemy equivalent

## 9. Testing & Quality ⭐
9.1 `pytest`: fixtures, parametrize, mocking (`unittest.mock`, `monkeypatch`)
9.2 Unit vs integration vs contract tests; testing LLM code (mock LLM, golden sets)
9.3 Coverage, linting (`ruff`, `black`, `flake8`), type checking (`mypy`)
9.4 SonarQube quality gates 🎯
9.5 Logging (`logging`, structured logs), 12-factor config

## 10. Packaging & Environment
10.1 `venv`, `pip`, `poetry`, `uv`, lock files
10.2 Dockerizing a Python app, multi-stage builds, slim images
10.3 Dependency management in Lambda (layers, container images)

## 11. Coding Round Practice
11.1 Arrays/strings, hashmaps, two pointers, sliding window
11.2 Sorting, searching, stacks/queues, recursion, basic DP
11.3 Practical tasks: rate limiter, LRU cache, retry with backoff, log parser, flatten JSON, paginated API client
11.4 Write an async worker pool; implement a simple tool-calling loop

## 12. Likely Questions (practice out loud)
- Explain the GIL and its impact on an LLM API service.
- How do you handle a blocking call inside an async FastAPI endpoint?
- Difference between `Depends` and middleware?
- How do you validate and retry bad LLM JSON?
- How would you structure a large FastAPI project?

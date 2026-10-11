# 02 — Whole Backend + AWS Interview Index
Covers: Job 1 (AWS migration, microservices, CI/CD, security) + Job 2 (AWS deployment of AI systems)
Legend: ⭐ likely | ⚠️ gap vs JD | 🎯 your resume hook

---

## 1. API Design ⭐
1.1 REST principles, resource naming, HTTP verbs/status codes, idempotency
1.2 Versioning, pagination (offset vs cursor), filtering, sorting
1.3 Error response standards, validation, rate limiting, throttling
1.4 REST vs GraphQL vs gRPC vs WebSockets
1.5 Swagger/OpenAPI documentation 🎯
1.6 Webhooks, idempotency keys, retries
1.7 🎯 Watermelon, Project IQ, ARKA APIs

## 2. Authentication & Security ⭐
2.1 JWT (access/refresh), OAuth2 flows, OIDC, Auth0, Firebase Auth, OTP 🎯
2.2 RBAC vs ABAC, multi-tenant isolation 🎯 (ARKA)
2.3 OWASP Top 10: SQL injection, XSS, CSRF, SSRF, broken access control
2.4 Encryption at rest/in transit, hashing (bcrypt/argon2), secrets management
2.5 AWS Secrets Manager, KMS, SSM Parameter Store ⚠️
2.6 LLM-specific security: prompt injection, data leakage, PII handling

## 3. Databases ⭐
3.1 SQL: joins, indexes, query plans (`EXPLAIN`), normalization, transactions, ACID
3.2 Isolation levels, locking, deadlocks
3.3 PostgreSQL deep points: JSONB, pgvector, partitioning, connection pooling (PgBouncer)
3.4 Schema design: multi-tenant (shared schema vs schema-per-tenant vs DB-per-tenant) 🎯 ARKA
3.5 Migrations, zero-downtime schema changes, data migration from legacy DB 🎯 Watermelon
3.6 ⚠️ **DynamoDB** (named in Job 1): partition/sort keys, GSI/LSI, single-table design, read/write capacity, hot partitions, query vs scan, TTL, streams
3.7 ⚠️ **RDS/Aurora**: Multi-AZ, read replicas, backups, parameter groups, RDS Proxy (Lambda connections)
3.8 SQL vs NoSQL: how to choose
3.9 Elasticsearch/Algolia search basics 🎯

## 4. Caching & Messaging
4.1 Redis: data types, TTL, eviction, cache-aside/write-through, invalidation 🎯 (30% latency gain)
4.2 Queues: SQS (standard vs FIFO, DLQ), SNS, EventBridge, Kafka basics ⚠️
4.3 Async job processing, scheduled jobs (cron, EventBridge Scheduler) 🎯 JIRA sync
4.4 Idempotent consumers, retries with backoff

## 5. Architecture & System Design ⭐
5.1 Monolith vs microservices, service boundaries, API gateway pattern
5.2 Sync vs async communication, saga, outbox, circuit breaker
5.3 Scalability: horizontal vs vertical, load balancing, stateless services
5.4 CAP theorem, eventual consistency
5.5 Design exercises to rehearse:
  - Multi-tenant conversational AI platform (ARKA)
  - NL2SQL service with safe execution
  - Document processing pipeline (upload → OCR → extract → validate)
  - URL shortener / rate limiter / notification service
5.6 Third-party integrations (Salesforce, HubSpot, JIRA, Razorpay, Twilio) — retry, webhooks, token refresh 🎯

## 6. AWS Services ⭐ (biggest gap area)
| Service | What to know | Status |
|---|---|---|
| Lambda | cold starts, concurrency, layers, timeouts, VPC access, event sources | 🎯 ConnectIQ |
| API Gateway | REST vs HTTP API, authorizers, throttling, stages, Lambda proxy | ⚠️ |
| ECS / Fargate | task def, service, ALB, autoscaling, task vs execution role | ⚠️ |
| ECR | image push/pull, scanning | ⚠️ |
| S3 | presigned URLs, lifecycle, versioning, event notifications | 🎯 |
| RDS / Aurora | see 3.7 | ⚠️ |
| DynamoDB | see 3.6 | ⚠️ |
| IAM | roles vs users, policies, least privilege, assume-role | ⚠️ |
| VPC | subnets, security groups vs NACLs, NAT, endpoints | ⚠️ |
| CloudWatch | logs, metrics, alarms, X-Ray tracing | ⚠️ |
| Amazon Connect / Transcribe / Polly | 🎯 ConnectIQ |
| Bedrock | see GenAI file | ⚠️ |
| Route 53 / ALB / CloudFront | DNS, load balancing, CDN | basic |
| Step Functions | orchestration vs Lambda chaining | ⚠️ |

Compare: Lambda vs ECS/Fargate — when to choose each (long-running agents, WebSockets, cold starts, cost).

## 7. Azure → AWS Migration ⚠️ (Job 1 headline task)
7.1 Service mapping: Azure Functions→Lambda, App Service/AKS→ECS/Fargate, APIM→API Gateway, Cosmos DB→DynamoDB, Azure SQL→RDS, Blob→S3, Key Vault→Secrets Manager, Azure AD→Cognito/IAM, Azure Monitor→CloudWatch, Azure DevOps→CodePipeline/GitHub Actions, Azure Document Intelligence→Textract (🎯 you used ADI in IIRM)
7.2 Assessment approach: inventory, dependency mapping, reusable vs rewrite, migration gaps
7.3 Strategies: rehost, replatform, refactor (the 6 Rs)
7.4 Data migration and cutover, rollback plan, testing parity 🎯 Watermelon legacy migration
7.5 Say-this-in-interview: "Here is how I'd approach the first 2 weeks of assessment."

## 8. CI/CD & DevOps ⭐
8.1 Pipeline stages: lint → test → build → scan → deploy → smoke test
8.2 GitHub Actions, Jenkins 🎯; CodePipeline/CodeBuild/CodeDeploy ⚠️
8.3 Docker: images, layers, compose, health checks
8.4 IaC: Terraform / CloudFormation / CDK / SAM ⚠️ (at least one basic example)
8.5 Deployment strategies: blue/green, canary, rolling
8.6 Environment config, secrets in pipelines, SonarQube gates 🎯
8.7 MLOps overlap: model/prompt versioning, eval in CI (see GenAI file)

## 9. Monitoring, Reliability, Networking
9.1 Logs, metrics, traces; structured logging (Winston 🎯)
9.2 SLI/SLO, alerting, health checks, on-call basics
9.3 Performance: profiling, slow queries, connection pools, load testing (k6/Locust)
9.4 Networking: HTTP/HTTPS, TLS, DNS, load balancers, security groups, private subnets
9.5 Debugging production incidents: a story to prepare

## 10. Collaboration & Process
10.1 Code review practices, technical documentation, ADRs
10.2 Working with frontend/data/DevOps teams
10.3 Achievements: Rising Star, Super Squad awards, hackathons — attach concrete impact

## 11. Likely Questions
- Walk me through migrating an Azure Function-based service to AWS.
- Lambda or Fargate for a FastAPI service with LLM calls taking 30–60s? Why?
- How would you secure an API Gateway + Lambda endpoint?
- Design a multi-tenant DB for a SaaS AI product.
- How did Redis cut your latency by 30%? How did you measure it?
- DynamoDB vs RDS for chat history/session memory?

# 3.4 – 3.5 Vector Databases and Index Types

Running example: the Acme Electronics policy docs in `rag/data/`.

---

## 1. What is a vector database?

In 3.3 we kept our 12 chunks in memory and compared the question against **every one** of them. That is fine for 12 chunks, or even 100,000.

Now imagine Amazon's help center: 50 million chunks. Comparing against every chunk on every question is too slow and too expensive.

A **vector database** is a database built for one job: **"Given this vector, find the closest vectors, fast."**

Analogy: our numpy search is reading every book in the library to find the right page. A vector database is a library with a smart catalog.

### What it stores for each chunk
| Field | Example |
|---|---|
| id | `refunds-opened-electronics-1` |
| vector | the 384 numbers |
| text | "Opened laptops, phones, and tablets can be returned within 15 days..." |
| metadata | `{source: "refunds.md", section: "Opened Electronics", tenant: "acme", updated: "2026-09-01"}` |

Metadata matters a lot. It gives you **citations** (where the answer came from) and **filters** (only search this customer's docs).

### Why not just use numpy forever?
A real vector DB also gives you:
- **Speed at scale** – smart indexes (section 2)
- **Saving to disk** – data survives a restart
- **Updates and deletes** – a policy changed, replace only that chunk
- **Filters** – "only search `tenant = acme` AND `updated after 2026`"
- **Many users at once** – handles many questions in parallel

---

## 2. Index types (3.5) – how the search gets fast

Key idea first: **fast vector search is approximate.** It finds *almost* the best matches, not guaranteed the best. This is called **ANN – Approximate Nearest Neighbor**.

**Recall** = out of the true top 10 matches, how many did the fast search actually find? 95% recall means it found 9.5 out of 10 on average.

Every index trades **speed vs recall vs memory**. You cannot max all three.

### Flat (brute force)
- Compares against every vector. This is what we did in 3.3.
- Recall: 100% (perfect).
- Speed: slow at large scale.
- Use when: under ~100k vectors, or to measure the true answers when testing other indexes.

### IVF (Inverted File Index) – "go to the right section of the library"
- At build time, group all vectors into clusters (say 1,000 groups of similar chunks).
- At search time: find the 10 closest **groups** first, then only search inside those groups.
- Analogy: you don't search the whole library for a cookbook. You walk to the Cooking section.
- Knobs:
  - `nlist` = how many groups
  - `nprobe` = how many groups to check per question. More = better recall, slower.
- Weakness: if the best match sits at the edge of a group you didn't check, you miss it.

### HNSW (Hierarchical Navigable Small World) – "highways, then local roads"
- The most popular index today. Default in pgvector, Qdrant, Weaviate, OpenSearch and others.
- Builds a **graph**: each vector is connected to its nearby neighbors.
- Has layers: the top layer has few points with long-distance links (highways), lower layers have more points with short links (local roads).
- Search: start on the highway, jump close to the right area, then walk local roads to the exact neighborhood.
- Analogy: driving from Delhi to a street in Bangalore. You take a flight, then a highway, then local streets. You never check every street in India.
- Knobs:
  - `M` = links per point. More = better recall, more memory.
  - `ef_construction` = effort while building. Higher = better graph, slower build.
  - `ef_search` = effort per question. Higher = better recall, slower answer. **This is the knob you tune in production.**
- Strengths: very fast, high recall (often 95–99%).
- Weaknesses: uses a lot of RAM (the graph lives in memory), slower to build, deletes are messy.

### PQ (Product Quantization) – "compress the vectors"
- Shrinks each vector, for example from 1,536 numbers (about 6 KB) down to a few dozen bytes.
- Analogy: storing a photo as a small JPEG instead of the raw file. Smaller, slightly less sharp.
- Often combined: **IVF-PQ** for billions of vectors where RAM is the limit.
- Cost: lower recall. Fix it by **re-scoring** the top results with the full vectors.

### Quick comparison
| Index | Speed | Recall | Memory | Use when |
|---|---|---|---|---|
| Flat | Slow at scale | 100% | Normal | Small data, testing |
| IVF | Fast | Good (tune `nprobe`) | Normal | Large data, cheaper RAM |
| HNSW | Very fast | Very high | High | Default choice for most apps |
| IVF-PQ | Fast | Lower | Very low | Billions of vectors |

### Memory math (seniors are expected to do this)
Each number is a 4-byte float.
- 1 million chunks × 768 numbers × 4 bytes ≈ **3 GB** just for vectors.
- HNSW graph adds roughly 10–30% more.
- 100 million chunks ≈ 300 GB → now you need compression (PQ), smaller embeddings, or a disk-based index.

---

## 3. The main options (3.4)

| Option | What it is | Best for | Watch out for |
|---|---|---|---|
| **pgvector** 🎯 | Extension that adds vectors to PostgreSQL | You already use Postgres; need SQL joins + vectors together; up to tens of millions of vectors | Tuning needed at large scale; heavy vector load can slow your main app DB |
| **Pinecone** 🎯 | Fully managed cloud vector DB | Zero ops, fast to start, serverless pricing | Vendor lock-in; cost grows with scale; data leaves your cloud |
| **OpenSearch / Elasticsearch** | Search engine with vector support | Need keyword (BM25) + vector search in one place; AWS-native (Amazon OpenSearch) | Heavier to run and tune |
| **Qdrant** | Open-source vector DB (Rust) | Strong filtering, self-host or cloud | Another system to operate |
| **Weaviate** | Open-source vector DB | Built-in hybrid search and modules | Another system to operate |
| **Milvus** | Open-source, built for huge scale | Billions of vectors | Complex to run |
| **Chroma** | Simple embedded DB | Prototypes, local dev, demos | Not the usual choice for large production |
| **FAISS** | A library from Meta, **not a database** | Fast in-memory search inside your own code | No saving, filters, or updates out of the box |
| **AWS options** | Bedrock Knowledge Bases (managed RAG), S3 Vectors (cheap vector storage in S3) | AWS shops that want managed services | Less control over chunking/retrieval details |

### How to choose (a simple decision path)
1. **Already on Postgres, under ~10–50M vectors?** → pgvector. One less system to run. Boring technology is a feature.
2. **Need keyword + vector search together?** → OpenSearch, Weaviate, or Qdrant.
3. **Small team, want zero ops, fine with managed cloud?** → Pinecone.
4. **Billions of vectors?** → Milvus, or a DB with PQ / disk-based indexes.
5. **Just prototyping?** → Chroma or plain numpy/FAISS.

> "Choose boring technology." – Dan McKinley. Adding a new database means new backups, monitoring, security reviews and on-call pain. Earn it.

---

## 4. Things seniors get asked about

### 4.1 Metadata filtering: pre-filter vs post-filter
Question: "Find chunks about refunds, but only for tenant `acme`."
- **Post-filter**: find the top 10 by vector, then drop non-acme ones. Problem: maybe 9 of 10 were other tenants' docs → you return 1 result.
- **Pre-filter**: limit to acme docs first, then search. Correct results, but can be slower if the filter is very narrow.
- Good DBs (Qdrant, pgvector with care, Pinecone) apply the filter **during** the search. Always ask how your DB does it.

### 4.2 Multi-tenancy (3.8) 🎯 ARKA
Many customers share one system. Customer A must **never** see Customer B's docs.
| Approach | Isolation | Cost | Use when |
|---|---|---|---|
| Shared index + `tenant_id` filter | Weakest (one bug = data leak) | Cheapest | Many small tenants |
| Namespace / collection per tenant | Good | Medium | Most SaaS apps |
| Separate DB per tenant | Strongest | Most expensive | Banks, healthcare, strict contracts |

Golden rule: **the tenant filter is added by your server code from the logged-in user, never by the LLM.** If the model can choose the tenant, a prompt injection can choose it too.

### 4.3 Changing the embedding model = re-index everything
Vectors from model A and model B live on **different maps**. You cannot compare them.
If you upgrade the embedding model, you must re-embed **every** chunk.
- Store `embedding_model` and version in metadata.
- Build the new index alongside the old one, test it, then switch traffic (blue-green).

### 4.4 Keeping data fresh
Policies change. Old chunks give wrong answers confidently.
- Store a `doc_hash` per document; re-embed only when the hash changes.
- On update: delete the old chunks for that doc, insert the new ones.
- Store `updated_at` so you can prefer or filter recent content.

### 4.5 Measure, don't guess
- **Recall@k**: compare ANN results against Flat (exact) results on a test set.
- **Latency p50 / p95 / p99**: typical and worst-case speed.
- **Cost per 1,000 queries** and **storage cost per month**.

---

## 5. Interview questions with short answers

**Q: Why use a vector DB instead of normal SQL?**
SQL finds exact matches ("price = 50"). A vector DB finds *similar meaning* ("money back" ≈ "refund"), and does it fast over millions of items using ANN indexes.

**Q: HNSW vs IVF?**
HNSW is a graph: very fast, high recall, but uses lots of RAM. IVF groups vectors into clusters: less memory, recall depends on how many groups you check. I default to HNSW and tune `ef_search`; I'd consider IVF-PQ when RAM cost becomes the problem.

**Q: Your search results got worse after adding more data. Why?**
Possible causes: ANN recall dropped (raise `ef_search` / `nprobe`), post-filtering removed results, more near-duplicate chunks crowding the top-k, or the index needs a rebuild. I'd measure recall against a Flat search to find out which.

**Q: pgvector or Pinecone?**
pgvector if we already run Postgres and want joins with business data and one less system. Pinecone if the team wants zero ops and the scale or growth justifies a managed service. Both are in my resume, so I'd give a real example of why each was chosen.

**Q: How do you keep tenants isolated?**
Namespace or collection per tenant, plus a server-side tenant filter taken from the auth token. Never let the LLM pick the tenant. Add tests that try to read across tenants.

**Q: How would you size a vector DB for 20M chunks?**
20M × 768 × 4 bytes ≈ 61 GB for raw vectors, plus ~20% for the HNSW graph ≈ 75 GB RAM. Options to cut it: smaller embeddings (384 dims), quantization, or a disk-based index.

---

## 6. One-paragraph summary to remember

A vector database stores chunks as number lists plus metadata, and finds the most similar ones fast. It's fast because it searches approximately using an index: **HNSW** (a graph, the default) or **IVF** (clusters), optionally compressed with **PQ**. Every choice trades speed, accuracy and memory. In real systems, the hard parts are not the index but **filtering, tenant isolation, keeping data fresh, and re-indexing when the embedding model changes.**

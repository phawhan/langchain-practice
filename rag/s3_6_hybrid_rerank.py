"""3.6 Hybrid search (keywords + meaning), metadata filtering, and reranking.

Run: .venv/bin/python rag/s3_6_hybrid_rerank.py
"""
import re

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from s3_3_embeddings import build_index, model, top_k

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")  # reads question + chunk together

chunks, vecs = build_index()
texts = [f"{c['source']} > {c['section']}\n{c['text']}" for c in chunks]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


bm25 = BM25Okapi([words(t) for t in texts])  # keyword index: rare matching words score high


def vector_search(q: str, k: int = 10, source: str | None = None) -> list[int]:
    """Search by meaning. `source` = metadata pre-filter: only search chunks from that file."""
    allowed = [i for i, c in enumerate(chunks) if source in (None, c["source"])]
    return [allowed[i] for i, _ in top_k(model.encode(q), vecs[allowed], k)]


def keyword_search(q: str, k: int = 10) -> list[int]:
    scores = bm25.get_scores(words(q))
    return sorted(range(len(texts)), key=lambda i: -scores[i])[:k]


def hybrid_search(q: str, k: int = 10, rrf_k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion: merge two ranked lists by position, not by raw score."""
    fused: dict[int, float] = {}
    for ranking in (vector_search(q), keyword_search(q)):
        for rank, i in enumerate(ranking):
            fused[i] = fused.get(i, 0) + 1 / (rrf_k + rank + 1)
    return sorted(fused, key=lambda i: -fused[i])[:k]


def rerank(q: str, candidates: list[int], k: int = 3) -> list[int]:
    scores = reranker.predict([(q, texts[i]) for i in candidates])
    return [i for _, i in sorted(zip(scores, candidates), reverse=True)][:k]


def show(name: str, ids: list[int]):
    top = [f"{n}. {chunks[i]['source'].removesuffix('.md')}/{chunks[i]['section']}" for n, i in enumerate(ids[:3], 1)]
    print(f"  {name:<16} {'   '.join(top)}")


if __name__ == "__main__":
    for q in ["I dropped my phone in water, am I covered?", "What is the AcmeCare deductible?"]:
        print(f"\nQ: {q}")
        show("vector", vector_search(q))
        show("keyword (BM25)", keyword_search(q))
        show("hybrid (RRF)", hybrid_search(q))
        show("hybrid + rerank", rerank(q, hybrid_search(q)))

    q = "How long does it take?"
    print(f"\nQ: {q}   (vague question: which 'it'?)")
    show("vector", vector_search(q))
    show("filter=shipping", vector_search(q, source="shipping.md"))
    show("filter=warranty", vector_search(q, source="warranty.md"))

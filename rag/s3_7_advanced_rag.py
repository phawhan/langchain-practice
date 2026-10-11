"""3.7 Advanced RAG - fix the question before searching, and give better context after.

No LLM key here, so LLM outputs are hand-written and marked "LLM would return". Searches are real.
Run: .venv/bin/python rag/s3_7_advanced_rag.py
"""
import re

from s3_3_embeddings import model, top_k
from s3_6_hybrid_rerank import chunks, hybrid_search, vector_search


def show(label: str, ids: list[int], n: int = 3) -> None:
    top = [f"{chunks[i]['source'].removesuffix('.md')}/{chunks[i]['section']}" for i in ids[:n]]
    print(f"  {label:<12} {'  |  '.join(top)}")


def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Merge many ranked lists by position (same idea as hybrid search in 3.6)."""
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, i in enumerate(ranking):
            fused[i] = fused.get(i, 0) + 1 / (k + rank + 1)
    return sorted(fused, key=lambda i: -fused[i])


def demo_rewrite() -> None:
    print("\n1. QUERY REWRITING - follow-up question, history: 'I bought AcmeCare for my phone'")
    q = "What if I break it twice?"
    rewritten = "How many accidental damage claims per year does AcmeCare allow?"  # LLM would return
    show("raw", hybrid_search(q))
    show("rewritten", hybrid_search(rewritten))


def demo_multi_query() -> None:
    print("\n2. MULTI-QUERY - one question, answer spread across several docs")
    q = "My new laptop arrived broken. What are my options?"
    variants = [  # LLM would return
        "Can I return a defective laptop for a refund?",
        "How do I file a warranty claim for a defective product?",
        "What happens if my package arrives damaged?",
    ]
    show("single", hybrid_search(q), 4)
    show("multi-query", rrf([hybrid_search(v) for v in [q, *variants]]), 4)


def demo_hyde() -> None:
    print("\n3. HyDE - search with a fake answer, because answers look like docs, questions don't")
    q = "phone fell in the pool"
    fake_answer = ("The standard warranty does not cover water damage or accidental damage. "
                   "An extended protection plan may cover accidents for a deductible.")  # LLM would return
    show("question", vector_search(q))
    show("fake answer", vector_search(fake_answer))


def demo_parent_child() -> None:
    print("\n4. PARENT-CHILD - search small sentences (precise), return the whole section (context)")
    kids = [(s, p) for p, c in enumerate(chunks)
            for s in re.split(r"(?<=\.)\s+", c["text"]) if len(s) > 30]
    vecs = model.encode([s for s, _ in kids])
    q = "Do I need to reset my device before returning it?"
    i, score = top_k(model.encode(q), vecs, 1)[0]
    sentence, parent = kids[i]
    print(f"  Q: {q}\n  child match ({score:.2f}): {sentence!r}")
    print(f"  parent sent to LLM:\n    {chunks[parent]['text'].replace(chr(10), chr(10) + '    ')}")


if __name__ == "__main__":
    demo_rewrite()
    demo_multi_query()
    demo_hyde()
    demo_parent_child()

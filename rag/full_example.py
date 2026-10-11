"""One question, end to end: search settings (stage 1) vs LLM writing settings (stage 2).

Run: .venv/bin/python rag/full_example.py
"""
import numpy as np

from s3_6_hybrid_rerank import chunks, hybrid_search, keyword_search, rerank, vector_search

Q = "Can I return my opened laptop?"


def name(i: int) -> str:
    return f"{chunks[i]['source'].removesuffix('.md')}/{chunks[i]['section']}"


def stage1_search(top_k: int = 5, final_n: int = 2) -> None:
    print(f"STAGE 1 - SEARCH  (retrieval top_k={top_k}, keep {final_n} after rerank)\nQ: {Q}")
    for label, ids in [("BM25 keyword", keyword_search(Q, top_k)), ("vector", vector_search(Q, top_k))]:
        print(f"  {label:<13}: {[name(i) for i in ids]}")
    merged = hybrid_search(Q, top_k)
    print(f"  {'hybrid (RRF)':<13}: {[name(i) for i in merged]}")
    print(f"  {'rerank':<13}: {[name(i) for i in rerank(Q, merged, final_n)]}  <- sent to the LLM")


# Stage 2 is a toy: real LLMs do this over ~100k possible words, once per word they write.
# The LLM has written "Yes, opened laptops can be returned within 15" and scores the next word.
WORDS = ["days", "business", "weeks", "minutes", "years", "banana"]
SCORES = np.array([5.0, 2.6, 2.1, 1.2, 0.8, -1.0])


def probs(temperature: float) -> np.ndarray:
    """Softmax: scores -> percentages. Low temperature sharpens, high temperature flattens."""
    z = np.exp((SCORES - SCORES.max()) / temperature)
    return z / z.sum()


def stage2_writing() -> None:
    print("\nSTAGE 2 - LLM WRITES  next word after '...returned within 15'")
    for t in (0.2, 1.0, 2.0):
        print(f"  temperature={t}: " + "  ".join(f"{w} {p:.0%}" for w, p in zip(WORDS, probs(t))))
    p = probs(2.0)
    order = np.argsort(-p)
    print(f"  top_k=3 keeps   : {[WORDS[i] for i in order[:3]]}")
    cutoff = np.searchsorted(np.cumsum(p[order]), 0.9) + 1  # smallest set adding up to 90%
    print(f"  top_p=0.9 keeps : {[WORDS[i] for i in order[:cutoff]]}")
    rng = np.random.default_rng(0)
    for t in (0.2, 2.0):
        print(f"  10 picks at temperature={t}: {[str(w) for w in rng.choice(WORDS, 10, p=probs(t))]}")


if __name__ == "__main__":
    stage1_search()
    stage2_writing()

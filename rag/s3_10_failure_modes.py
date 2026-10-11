"""3.10 RAG failure modes - reproduce common production failures, then apply the fix.

Run: .venv/bin/python rag/s3_10_failure_modes.py
"""
import hashlib

import numpy as np

from s3_3_embeddings import build_index, model, top_k


class Index:
    """Tiny vector index that stores a fingerprint (hash) per doc to detect changed content."""

    def __init__(self):
        self.text, self.hash, self.vec = {}, {}, {}

    def upsert(self, doc_id: str, text: str) -> bool:
        h = hashlib.sha256(text.encode()).hexdigest()
        if self.hash.get(doc_id) == h:
            return False  # unchanged: skip the embedding cost
        self.text[doc_id], self.hash[doc_id], self.vec[doc_id] = text, h, model.encode(text)
        return True

    def search(self, q: str, k: int = 3) -> list[str]:
        ids = list(self.text)
        return [ids[i] for i, _ in top_k(model.encode(q), np.array([self.vec[d] for d in ids]), k)]


def demo_stale():
    print("1. STALE DATA - the policy changed, the index did not")
    source = {"refunds": "Items can be returned within 30 days.", "shipping": "Standard shipping is free over $50."}
    idx = Index()
    for d, t in source.items():
        idx.upsert(d, t)
    source["refunds"] = "Items can be returned within 45 days."  # policy team edits the doc
    print(f"  index says : {idx.text[idx.search('return window', 1)[0]]!r}")
    changed = [d for d, t in source.items() if idx.upsert(d, t)]  # sync job (cron / doc-change event)
    print(f"  after sync : {idx.text['refunds']!r}  (re-embedded only {changed})")


def demo_duplicates():
    print("\n2. DUPLICATES - the same text copied on 3 pages fills the whole top 3")
    idx = Index()
    for page in ["faq", "help-center", "checkout-page"]:
        idx.upsert(page, "Express shipping takes 1-2 business days and costs $15.")
    idx.upsert("lost", "If tracking shows no movement for 7 days, contact support.")
    print(f"  top 3      : {idx.search('shipping speed and tracking')}")
    unique = {h: d for d, h in reversed(idx.hash.items())}  # dedup: one doc per identical hash
    print(f"  after dedup: {len(idx.hash)} docs -> {len(unique)} docs")


def demo_no_answer(threshold: float = 0.4):
    print(f"\n3. NO ANSWER IN DOCS - refuse when the best score < {threshold}")
    chunks, vecs = build_index()
    for q in ["Can I return an opened laptop?", "What time does your store open on Sunday?",
              "I dropped my phone in water, am I covered?"]:
        i, score = top_k(model.encode(q), vecs, 1)[0]
        verdict = f"answer from {chunks[i]['section']}" if score >= threshold else "say 'I don't know' / hand to human"
        print(f"  {score:.2f}  {q:<44} -> {verdict}")


def lost_in_middle_order(ranked: list[str]) -> list[str]:
    """LLMs read the start and end of the prompt best: put the best chunks there, weakest in the middle."""
    return ranked[::2] + ranked[1::2][::-1]


if __name__ == "__main__":
    demo_stale()
    demo_duplicates()
    demo_no_answer()
    print("\n4. LOST IN THE MIDDLE - reorder chunks before building the prompt")
    print(f"  ranked best->worst: {['#1', '#2', '#3', '#4', '#5']}")
    print(f"  prompt order      : {lost_in_middle_order(['#1', '#2', '#3', '#4', '#5'])}")

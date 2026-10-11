"""3.9 RAG evaluation - measure retrieval quality on a golden dataset instead of guessing.

Run: .venv/bin/python rag/s3_9_evaluation.py
"""
from s3_6_hybrid_rerank import chunks, hybrid_search, keyword_search, rerank, vector_search

# Golden dataset: real-style questions + the section(s) a correct search must find.
GOLDEN = [
    ("Can I return an opened laptop?", {"Opened Electronics"}),
    ("I dropped my phone in water, am I covered?", {"Standard Warranty", "Extended Warranty"}),
    ("my parcel hasn't moved in a week", {"Lost Packages"}),
    ("What is the AcmeCare deductible?", {"Extended Warranty"}),
    ("Can I return a gift card?", {"Exceptions"}),
    ("How much is express shipping?", {"Delivery Options"}),
    ("Do you ship batteries overseas?", {"International Orders"}),
    ("How long until my refund shows up?", {"Standard Refunds"}),
    ("What do I need to file a warranty claim?", {"Claims"}),
    ("Who pays customs fees on international orders?", {"International Orders"}),
    ("Is there a fee if I return a used tablet?", {"Opened Electronics"}),
    ("How long is the warranty on Acme products?", {"Standard Warranty"}),
]

METHODS = {
    "vector": vector_search,
    "keyword (BM25)": keyword_search,
    "hybrid (RRF)": hybrid_search,
    "hybrid + rerank": lambda q: rerank(q, hybrid_search(q), 10),
}


def first_hit_rank(ids: list[int], expected: set[str]) -> int | None:
    """Position (1 = top) of the first correct section, or None if it was never found."""
    for rank, i in enumerate(ids, 1):
        if chunks[i]["section"] in expected:
            return rank
    return None


if __name__ == "__main__":
    print(f"{'method':<17}{'Hit@1':>7}{'Hit@3':>7}{'MRR':>7}   misses (not in top 3)")
    for name, search in METHODS.items():
        ranks = [first_hit_rank(search(q), expected) for q, expected in GOLDEN]
        hit1 = sum(r == 1 for r in ranks) / len(GOLDEN)
        hit3 = sum(r is not None and r <= 3 for r in ranks) / len(GOLDEN)
        mrr = sum(1 / r for r in ranks if r) / len(GOLDEN)
        misses = [q[:28] for (q, _), r in zip(GOLDEN, ranks) if not r or r > 3]
        print(f"{name:<17}{hit1:>7.0%}{hit3:>7.0%}{mrr:>7.2f}   {misses}")

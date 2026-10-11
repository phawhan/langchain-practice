"""3.3 Embeddings + similarity metrics - turn text into vectors that capture meaning.

Run: .venv/bin/python rag/s3_3_embeddings.py
"""
import numpy as np
from sentence_transformers import SentenceTransformer

from s3_2_chunking import DATA, markdown_chunks

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dims, ~90MB, runs on CPU


def top_k(query_vec: np.ndarray, doc_vecs: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Brute-force nearest neighbours: cosine against every chunk, keep the best k."""
    scores = doc_vecs @ query_vec / (np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(query_vec))
    best = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in best]


def demo_meaning():
    """Same meaning -> nearby vectors, even with zero shared words."""
    texts = ["refund policy", "getting my money back", "pizza recipe"]
    v = model.encode(texts)
    print(f"Each text -> {v.shape[1]} numbers, e.g. {v[0][:4].round(3)}...")
    for i, j in [(0, 1), (0, 2)]:
        cos = v[i] @ v[j] / (np.linalg.norm(v[i]) * np.linalg.norm(v[j]))
        print(f"  cos({texts[i]!r}, {texts[j]!r}) = {cos:.2f}")


def demo_metrics():
    """Cosine vs dot vs L2: once vectors are normalized, all three rank identically."""
    a, b = model.encode(["return a laptop", "send back a computer"])
    cos = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)  # normalize to length 1
    l2 = np.linalg.norm(a - b)
    print(f"\n  cosine={cos:.3f}  dot(normalized)={a @ b:.3f}  L2={l2:.3f}")
    print(f"  identity: L2^2 = 2 - 2*cos -> {l2**2:.3f} == {2 - 2 * cos:.3f}")


def build_index():
    chunks = [c for f in sorted(DATA.glob("*.md")) for c in markdown_chunks(f.read_text(), f.name)]
    texts = [f"{c['source']} > {c['section']}\n{c['text']}" for c in chunks]  # prefix = context
    return chunks, model.encode(texts)


def search(query: str, chunks, vecs, k: int = 3):
    print(f"\nQ: {query}")
    for i, score in top_k(model.encode(query), vecs, k):
        print(f"  {score:.2f}  [{chunks[i]['source']} > {chunks[i]['section']}]")


if __name__ == "__main__":
    demo_meaning()
    demo_metrics()
    chunks, vecs = build_index()
    print(f"\nIndexed {len(chunks)} chunks -> matrix {vecs.shape}")
    search("Can I get my money back for a laptop I already opened?", chunks, vecs)
    search("my parcel hasn't moved in a week", chunks, vecs)
    search("I dropped my phone in water, am I covered?", chunks, vecs)

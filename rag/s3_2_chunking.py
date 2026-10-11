"""3.2 Chunking - split documents into pieces small enough to retrieve precisely.

Run: .venv/bin/python rag/s3_2_chunking.py
"""
import re
from pathlib import Path

DATA = Path(__file__).parent / "data"
SEPARATORS = ["\n\n", "\n", ". ", " "]  # biggest natural boundary first


def fixed_chunks(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    """Cut every `size` chars, repeating `overlap` chars so no fact is split clean in two."""
    step = size - overlap
    return [text[i : i + size] for i in range(0, max(len(text) - overlap, 1), step)]


def recursive_chunks(text: str, size: int = 200, seps: list[str] = SEPARATORS) -> list[str]:
    """Split on paragraphs; if a piece is still too big, retry with lines, then sentences, then words."""
    if len(text) <= size:
        return [text.strip()] if text.strip() else []
    if not seps:
        return fixed_chunks(text, size, 0)
    sep, rest = seps[0], seps[1:]
    chunks, buf = [], ""
    for piece in text.split(sep):
        candidate = f"{buf}{sep}{piece}" if buf else piece
        if len(candidate) <= size:
            buf = candidate  # keep packing pieces into the current chunk
            continue
        if buf.strip():
            chunks.append(buf.strip())
        buf = ""
        if len(piece) > size:
            chunks.extend(recursive_chunks(piece, size, rest))
        else:
            buf = piece
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def markdown_chunks(text: str, source: str, size: int = 300) -> list[dict]:
    """Structure-aware: split on ## headings and tag each chunk with doc + section."""
    out = []
    for block in re.split(r"\n(?=## )", text):
        section = block.splitlines()[0].lstrip("# ").strip()
        for chunk in recursive_chunks(block, size):
            out.append({"source": source, "section": section, "text": chunk})
    return out


if __name__ == "__main__":
    doc = (DATA / "refunds.md").read_text()
    for name, chunks in [("FIXED", fixed_chunks(doc)), ("RECURSIVE", recursive_chunks(doc))]:
        print(f"\n===== {name}: {len(chunks)} chunks =====")
        for c in chunks:
            print(f"--- {c!r}")
    print("\n===== MARKDOWN (structure-aware) =====")
    for c in markdown_chunks(doc, "refunds.md"):
        print(f"--- [{c['source']} > {c['section']}] {c['text'][:70]!r}...")

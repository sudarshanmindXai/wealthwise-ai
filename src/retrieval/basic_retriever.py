import json
import glob
import os


def load_chunks(base_dir="data/knowledge"):
    """
    Loads all JSONL knowledge chunks as per DATA_CONTRACT.md
    """
    chunks = []
    files = glob.glob(os.path.join(base_dir, "**/*.jsonl"), recursive=True)

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = obj.get("text")
                if not isinstance(text, str) or not text.strip():
                    continue

                chunks.append({
                    "file": file_path,
                    "line_no": line_no,
                    "doc_id": obj.get("doc_id"),
                    "doc_type": obj.get("doc_type"),
                    "itr_form": obj.get("itr_form"),  # may be None
                    "text": text
                })

    return chunks


def search(chunks, query, top_k=5, itr_form=None):
    """
    Simple keyword-based retrieval with optional ITR scoping
    """
    tokens = [t.lower() for t in query.replace("-", " ").split()]
    scored = []

    for chunk in chunks:
        if itr_form:
            if str(chunk.get("itr_form", "")).upper() != itr_form.upper():
                continue

        text = chunk["text"].lower()
        score = sum(1 for t in tokens if t in text)

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


if __name__ == "__main__":
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    query = "who should file ITR-2"
    results = search(chunks, query, top_k=3, itr_form="ITR-2")

    print("\nTop matches:\n")
    for r in results:
        print("-" * 40)
        print("Doc ID:", r["doc_id"])
        print("File:", r["file"])
        print("Line:", r["line_no"])
        print("Text:", r["text"][:300])
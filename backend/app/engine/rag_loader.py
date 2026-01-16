"""
WealthWise AI - RAG Document Loader
====================================
Loads semantically chunked JSONL legal documents into ChromaDB.
"""

import json
from pathlib import Path
from typing import Iterator
from dataclasses import dataclass


@dataclass
class LegalChunk:
    """Represents a single semantic chunk from legal documents"""
    doc_id: str
    doc_type: str  # act, rules, circular, bill
    text: str
    
    # Metadata for filtering
    section: str | None = None
    sub_section: str | None = None
    chapter: str | None = None
    paragraph: str | None = None
    circular_no: str | None = None
    ay: list[str] | None = None  # Assessment years
    section_type: str | None = None  # intro, paragraph, table, form
    
    def to_metadata(self) -> dict:
        """Convert to ChromaDB-compatible metadata"""
        return {
            k: v for k, v in {
                "doc_id": self.doc_id,
                "doc_type": self.doc_type,
                "section": self.section,
                "sub_section": self.sub_section,
                "chapter": self.chapter,
                "paragraph": self.paragraph,
                "circular_no": self.circular_no,
                "ay": ",".join(self.ay) if self.ay else None,
                "section_type": self.section_type,
            }.items() if v is not None
        }


def load_jsonl_file(file_path: Path) -> Iterator[LegalChunk]:
    """
    Load a single JSONL file and yield LegalChunk objects.
    Handles both IT Act structure and Circular structure.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping line {line_num} in {file_path}: {e}")
                continue
            
            # Required fields
            doc_id = data.get("doc_id", f"unknown_{line_num}")
            doc_type = data.get("doc_type", "unknown")
            text = data.get("text", "")
            
            if not text:
                continue
            
            yield LegalChunk(
                doc_id=doc_id,
                doc_type=doc_type,
                text=text,
                section=data.get("section"),
                sub_section=data.get("sub_section"),
                chapter=data.get("chapter"),
                paragraph=data.get("paragraph"),
                circular_no=data.get("circular_no"),
                ay=data.get("ay"),
                section_type=data.get("section_type"),
            )


def load_all_legal_docs(base_dir: Path) -> Iterator[LegalChunk]:
    """
    Load all JSONL files from the legal_docs directory.
    """
    for jsonl_file in base_dir.rglob("*.jsonl"):
        print(f"Loading: {jsonl_file}")
        yield from load_jsonl_file(jsonl_file)


def get_stats(base_dir: Path) -> dict:
    """Get statistics about loaded documents"""
    stats = {
        "total_chunks": 0,
        "by_doc_type": {},
        "by_file": {},
    }
    
    for jsonl_file in base_dir.rglob("*.jsonl"):
        file_count = 0
        for chunk in load_jsonl_file(jsonl_file):
            stats["total_chunks"] += 1
            file_count += 1
            
            doc_type = chunk.doc_type
            stats["by_doc_type"][doc_type] = stats["by_doc_type"].get(doc_type, 0) + 1
        
        stats["by_file"][jsonl_file.name] = file_count
    
    return stats


# =============================================================================
# Direct execution for testing
# =============================================================================

if __name__ == "__main__":
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent.parent / "data" / "legal_docs"
    
    print("=" * 60)
    print("WealthWise AI - Legal Document Loader")
    print("=" * 60)
    
    if not base_dir.exists():
        print(f"Error: Directory not found: {base_dir}")
        exit(1)
    
    stats = get_stats(base_dir)
    
    print(f"\nTotal chunks: {stats['total_chunks']}")
    print("\nBy document type:")
    for doc_type, count in sorted(stats["by_doc_type"].items()):
        print(f"  {doc_type}: {count}")
    
    print("\nBy file:")
    for file_name, count in sorted(stats["by_file"].items()):
        print(f"  {file_name}: {count}")
    
    # Sample first chunk
    print("\n" + "=" * 60)
    print("Sample chunk:")
    print("=" * 60)
    for chunk in load_all_legal_docs(base_dir):
        print(f"doc_id: {chunk.doc_id}")
        print(f"doc_type: {chunk.doc_type}")
        print(f"section: {chunk.section}")
        print(f"text (first 200 chars): {chunk.text[:200]}...")
        break

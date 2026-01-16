"""
WealthWise AI - Vector Store (ChromaDB)
=======================================
Manages the RAG vector database for legal document retrieval.
"""

import os
from pathlib import Path
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Run: pip install chromadb")

from .rag_loader import load_all_legal_docs, LegalChunk


# Default paths
DEFAULT_PERSIST_DIR = Path(__file__).parent.parent.parent / "data" / "chroma"
DEFAULT_LEGAL_DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "legal_docs"

# Collection name
LEGAL_COLLECTION = "legal_docs"


class VectorStore:
    """ChromaDB-based vector store for RAG"""
    
    def __init__(self, persist_dir: Optional[Path] = None):
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")
        
        self.persist_dir = persist_dir or DEFAULT_PERSIST_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        
        self._collection = None
    
    @property
    def collection(self):
        """Get or create the legal docs collection"""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=LEGAL_COLLECTION,
                metadata={"description": "WealthWise AI Legal Documents"}
            )
        return self._collection
    
    def ingest_legal_docs(
        self,
        legal_docs_dir: Optional[Path] = None,
        batch_size: int = 100,
    ) -> int:
        """
        Ingest all legal documents into ChromaDB.
        
        Args:
            legal_docs_dir: Path to legal docs directory
            batch_size: Number of documents to insert at once
        
        Returns:
            Number of documents ingested
        """
        legal_docs_dir = legal_docs_dir or DEFAULT_LEGAL_DOCS_DIR
        
        # Collect chunks in batches
        ids = []
        documents = []
        metadatas = []
        count = 0
        
        for chunk in load_all_legal_docs(legal_docs_dir):
            ids.append(chunk.doc_id)
            documents.append(chunk.text)
            metadatas.append(chunk.to_metadata())
            count += 1
            
            if len(ids) >= batch_size:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                )
                ids, documents, metadatas = [], [], []
                print(f"  Ingested {count} chunks...")
        
        # Final batch
        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
        
        return count
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        doc_type: Optional[str] = None,
        section: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for relevant legal documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            doc_type: Filter by document type (act, rules, circular)
            section: Filter by section number
        
        Returns:
            List of results with text and metadata
        """
        # Build filter
        where = None
        if doc_type or section:
            conditions = []
            if doc_type:
                conditions.append({"doc_type": doc_type})
            if section:
                conditions.append({"section": section})
            
            if len(conditions) == 1:
                where = conditions[0]
            else:
                where = {"$and": conditions}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )
        
        # Format results
        formatted = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "id": results["ids"][0][i] if results["ids"] else None,
                })
        
        return formatted
    
    def get_by_section(self, section: str) -> list[dict]:
        """Get all chunks for a specific section"""
        results = self.collection.get(
            where={"section": section},
        )
        
        formatted = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                formatted.append({
                    "text": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    "id": results["ids"][i] if results["ids"] else None,
                })
        
        return formatted
    
    def count(self) -> int:
        """Get total number of documents in collection"""
        return self.collection.count()
    
    def clear(self):
        """Clear all documents from collection"""
        self.client.delete_collection(LEGAL_COLLECTION)
        self._collection = None


# =============================================================================
# CLI for ingestion
# =============================================================================

def main():
    """CLI entry point for document ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WealthWise RAG Vector Store")
    parser.add_argument("--ingest", action="store_true", help="Ingest legal documents")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--count", action="store_true", help="Show document count")
    parser.add_argument("--clear", action="store_true", help="Clear all documents")
    
    args = parser.parse_args()
    
    store = VectorStore()
    
    if args.clear:
        print("Clearing vector store...")
        store.clear()
        print("Done!")
    
    if args.ingest:
        print("Ingesting legal documents...")
        count = store.ingest_legal_docs()
        print(f"Ingested {count} documents")
    
    if args.count:
        print(f"Total documents: {store.count()}")
    
    if args.search:
        print(f"Searching for: {args.search}")
        results = store.search(args.search)
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"ID: {r['id']}")
            print(f"Text: {r['text'][:200]}...")
            print(f"Metadata: {r['metadata']}")


if __name__ == "__main__":
    main()

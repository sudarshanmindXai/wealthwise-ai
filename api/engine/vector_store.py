"""
WealthWise AI - Vector Store (ChromaDB Implementation)
========================================================
Semantic search over Indian tax law knowledge base using ChromaDB.

Features:
- Load JSONL knowledge from data/knowledge/
- Embed using sentence-transformers
- Persist to disk
- Semantic search for tax queries
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import hashlib


@dataclass
class SearchResult:
    """A single search result"""
    content: str
    source: str
    section: Optional[str] = None
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorStore:
    """
    ChromaDB-based vector store for tax law retrieval.
    
    Uses sentence-transformers for embeddings and ChromaDB for storage.
    Falls back to keyword search if ChromaDB is unavailable.
    """
    
    COLLECTION_NAME = "wealthwise_tax_knowledge"
    PERSIST_DIR = Path(__file__).parent.parent.parent / "data" / "chroma_db"
    KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"
    
    def __init__(self, use_gpu: bool = False):
        self._client = None
        self._collection = None
        self._embedding_fn = None
        self._initialized = False
        self._use_gpu = use_gpu
        
        # Try to initialize ChromaDB
        self._init_chromadb()
    
    def _init_chromadb(self):
        """Initialize ChromaDB with sentence-transformers embeddings"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persist directory
            self.PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            
            # Initialize client with persistence
            self._client = chromadb.PersistentClient(
                path=str(self.PERSIST_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Try to use sentence-transformers embedding
            try:
                from chromadb.utils import embedding_functions
                self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2",
                    device="cuda" if self._use_gpu else "cpu"
                )
            except Exception as e:
                print(f"Warning: Could not load sentence-transformers: {e}")
                print("Using default ChromaDB embeddings")
                self._embedding_fn = None
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self._embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._initialized = True
            print(f"VectorStore initialized. Collection has {self._collection.count()} documents.")
            
        except ImportError as e:
            print(f"ChromaDB not available: {e}")
            print("VectorStore will use fallback keyword search.")
        except Exception as e:
            print(f"Error initializing VectorStore: {e}")
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @property
    def document_count(self) -> int:
        if self._collection:
            return self._collection.count()
        return 0
    
    def index_knowledge_base(self, force_reindex: bool = False) -> int:
        """
        Index all JSONL files from the knowledge directory.
        
        Args:
            force_reindex: If True, delete existing collection and reindex
        
        Returns:
            Number of documents indexed
        """
        if not self._initialized:
            print("VectorStore not initialized. Cannot index.")
            return 0
        
        # Check if already indexed
        if self._collection.count() > 0 and not force_reindex:
            print(f"Collection already has {self._collection.count()} documents. Use force_reindex=True to reindex.")
            return self._collection.count()
        
        # Delete and recreate if forcing
        if force_reindex and self._collection.count() > 0:
            self._client.delete_collection(self.COLLECTION_NAME)
            self._collection = self._client.create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self._embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Find all JSONL files
        jsonl_files = list(self.KNOWLEDGE_DIR.rglob("*.jsonl"))
        
        if not jsonl_files:
            print(f"No JSONL files found in {self.KNOWLEDGE_DIR}")
            return 0
        
        total_indexed = 0
        batch_size = 100
        
        for jsonl_path in jsonl_files:
            source_name = jsonl_path.stem
            print(f"Indexing {source_name}...")
            
            documents = []
            metadatas = []
            ids = []
            
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    try:
                        obj = json.loads(line.strip())
                        
                        # Extract content (handle different JSONL schemas)
                        content = obj.get('content') or obj.get('text') or obj.get('chunk') or str(obj)
                        
                        # Generate unique ID
                        doc_id = hashlib.md5(f"{source_name}_{line_num}_{content[:50]}".encode()).hexdigest()
                        
                        # Metadata
                        raw_meta = {
                            "source": source_name,
                            "line_num": line_num,
                            "section": obj.get('section', obj.get('title', '')),
                        }
                        
                        # Sanitize metadata (ChromaDB doesn't like None)
                        metadata = {k: (v if v is not None else "") for k, v in raw_meta.items()}
                        
                        documents.append(content[:8000])  # Limit chunk size
                        metadatas.append(metadata)
                        ids.append(doc_id)
                        
                        # Batch insert
                        if len(documents) >= batch_size:
                            self._collection.add(
                                documents=documents,
                                metadatas=metadatas,
                                ids=ids
                            )
                            total_indexed += len(documents)
                            documents, metadatas, ids = [], [], []
                            
                    except json.JSONDecodeError:
                        continue
            
            # Insert remaining
            if documents:
                self._collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                total_indexed += len(documents)
        
        print(f"Indexed {total_indexed} documents from {len(jsonl_files)} files.")
        return total_indexed
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_source: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Semantic search for relevant tax law passages.
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            filter_source: Optional filter by source file (e.g., "income_tax_act")
        
        Returns:
            List of SearchResult objects
        """
        if not self._initialized or self._collection.count() == 0:
            return self._fallback_search(query, n_results)
        
        # Build filter
        where_filter = None
        if filter_source:
            where_filter = {"source": filter_source}
        
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    search_results.append(SearchResult(
                        content=doc,
                        source=meta.get('source', 'unknown'),
                        section=meta.get('section', ''),
                        score=1 - distance,  # Convert distance to similarity
                        metadata=meta
                    ))
            
            return search_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, n_results)
    
    def _fallback_search(self, query: str, n_results: int) -> List[SearchResult]:
        """
        Keyword-based fallback search when ChromaDB is unavailable.
        """
        results = []
        query_lower = query.lower()
        keywords = query_lower.split()
        
        for jsonl_path in self.KNOWLEDGE_DIR.rglob("*.jsonl"):
            try:
                with open(jsonl_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        obj = json.loads(line.strip())
                        content = str(obj.get('content') or obj.get('text') or obj)
                        
                        # Check keyword match
                        content_lower = content.lower()
                        matches = sum(1 for kw in keywords if kw in content_lower)
                        
                        if matches > 0:
                            score = matches / len(keywords)
                            results.append(SearchResult(
                                content=content[:2000],
                                source=jsonl_path.stem,
                                section=obj.get('section', ''),
                                score=score,
                                metadata={"match_type": "keyword"}
                            ))
            except Exception:
                continue
        
        # Sort by score and return top N
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:n_results]


# Convenience function
def get_vector_store() -> VectorStore:
    """Get or create singleton VectorStore instance"""
    if not hasattr(get_vector_store, '_instance'):
        get_vector_store._instance = VectorStore()
    return get_vector_store._instance

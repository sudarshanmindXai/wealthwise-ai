"""
WealthWise AI - Reasoning Engine
================================
Adds legal context and citations to tax insights using RAG.
"""

from typing import List
from ..guardians.base import Insight
from .vector_store import get_vector_store

class ReasoningEngine:
    def __init__(self):
        self.vector_store = get_vector_store()
        
    def enrich_insights(self, insights: List[Insight]) -> List[Insight]:
        """
        Enhance insights with legal citations from the knowledge base.
        """
        if not self.vector_store.is_initialized:
            # Try once to index if empty? Or just skip? 
            # For now, if not initialized, we can't search.
            # Assuming main app startup initializes it or it lazy inits.
            if self.vector_store.document_count == 0:
                print("ReasoningEngine: Vector store empty, skipping enrichment.")
                return insights

        enriched = []
        for insight in insights:
            try:
                # Formulate query
                query = f"{insight.title} {insight.description}"
                
                # Search
                results = self.vector_store.search(query, n_results=1)
                
                if results:
                    top_result = results[0]
                    # Threshold for relevance
                    if top_result.score > 0.3: # Adjust based on distance metric
                        insight.legal_reference = f"{top_result.section} ({top_result.source})"
                        insight.legal_text = top_result.content[:500] + "..." if len(top_result.content) > 500 else top_result.content
                
            except Exception as e:
                print(f"ReasoningEngine Error for '{insight.title}': {e}")
            
            enriched.append(insight)
            
        return enriched

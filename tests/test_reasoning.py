
import sys
import os
import pytest
from api.engine.reasoning import ReasoningEngine
from api.guardians.base import Insight

# Mock VectorStore to avoid dependency on real DB/Network
class MockVectorStore:
    def __init__(self):
        self.is_initialized = True
        self.document_count = 100
        
    def search(self, query, n_results=1):
        from api.engine.vector_store import SearchResult # Import locally to ensure class availability
        if "80C" in query:
            return [SearchResult(
                content="Section 80C provides deduction for investments...",
                source="Income Tax Act",
                section="Section 80C",
                score=0.9
            )]
        return []

def test_reasoning_enrichment(monkeypatch):
    # Monkeypatch get_vector_store to return our mock
    import api.engine.reasoning
    monkeypatch.setattr(api.engine.reasoning, "get_vector_store", lambda: MockVectorStore())
    
    engine = ReasoningEngine()
    
    insights = [
        Insight(
            title="Maximize 80C",
            description="Invest in PPF to save tax under 80C",
            impact_currency=15000,
            confidence=1.0,
            category="deduction"
        ),
        Insight(
            title="Generic Tip",
            description="Save money",
            impact_currency=0,
            confidence=0.5,
            category="info"
        )
    ]
    
    enriched = engine.enrich_insights(insights)
    
    # Check first insight (should be enriched)
    assert enriched[0].legal_reference is not None
    assert "Section 80C" in enriched[0].legal_reference
    assert enriched[0].legal_text is not None
    
    # Check second insight (should not be enriched)
    assert enriched[1].legal_reference is None

"""
WealthWise AI - Query Router
=============================
Routes user queries to the appropriate handler:
- Calculator: For numerical tax calculations
- RAG: For legal/procedural questions
- Hybrid: For questions needing both computation + context

Examples:
- "What's my tax if I earn 15L?" -> Calculator
- "What is Section 80C?" -> RAG
- "Can I claim HRA without rent receipts?" -> RAG
- "Compare old vs new regime for me" -> Calculator + RAG context
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re

from .vector_store import VectorStore, SearchResult, get_vector_store
from .calculator import calculate_tax, compare_regimes, calculate_comprehensive_tax


class QueryType(Enum):
    CALCULATOR = "calculator"
    RAG = "rag"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


@dataclass
class RouterResult:
    """Result of query routing"""
    query_type: QueryType
    calculator_result: Optional[Any] = None
    rag_results: Optional[List[SearchResult]] = None
    combined_answer: Optional[str] = None
    confidence: float = 0.0


# Patterns for calculator queries
CALCULATOR_PATTERNS = [
    r"(?:what(?:'s| is)|calculate|compute|find)(?: my)? tax (?:for|if|on|with)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
    r"(?:₹|rs\.?|inr)?\s*([\d,]+)(?:\s*(?:lakh|lac|l|crore|cr))?\s*(?:income|salary)",
    r"compare.+(?:old|new).+regime",
    r"(?:which|what) regime.+better",
    r"(?:how much|what).+tax.+(?:pay|owe|liability)",
    r"(?:old|new) regime.+(?:tax|better|save)",
    r"(?:hra|80c|80d).+(?:exemption|deduction|claim|limit)",
]

# Patterns for RAG queries
RAG_PATTERNS = [
    r"what is.+(?:section|rule|act|chapter)",
    r"(?:explain|define|meaning of).+",
    r"(?:can i|am i (?:eligible|allowed)|is it (?:possible|allowed))",
    r"(?:documents?|proof|evidence) (?:required|needed)",
    r"(?:deadline|due date|last date)",
    r"(?:penalty|fine|consequence)",
    r"(?:procedure|process|steps|how to)",
    r"(?:who|which|when|where).+(?:required|applicable|eligible)",
]


class QueryRouter:
    """
    Routes queries to the appropriate handler based on intent classification.
    """
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self._vector_store = vector_store or get_vector_store()
    
    def classify(self, query: str) -> QueryType:
        """
        Classify query intent.
        
        Args:
            query: User's natural language query
        
        Returns:
            QueryType enum indicating the handler
        """
        query_lower = query.lower()
        
        # Check for calculator patterns
        calc_matches = sum(1 for p in CALCULATOR_PATTERNS if re.search(p, query_lower))
        
        # Check for RAG patterns
        rag_matches = sum(1 for p in RAG_PATTERNS if re.search(p, query_lower))
        
        # Check for numbers (suggests calculation)
        has_numbers = bool(re.search(r'\d{4,}', query.replace(',', '')))
        
        # Decision logic
        if calc_matches > 0 and has_numbers:
            return QueryType.CALCULATOR
        elif calc_matches > 0 and rag_matches > 0:
            return QueryType.HYBRID
        elif rag_matches > 0:
            return QueryType.RAG
        elif calc_matches > 0:
            return QueryType.CALCULATOR
        elif has_numbers:
            return QueryType.CALCULATOR
        else:
            return QueryType.RAG  # Default to RAG for general questions
    
    def extract_income(self, query: str) -> Optional[float]:
        """Extract income amount from query"""
        query = query.replace(',', '')
        
        # Match patterns like "15 lakh", "15L", "1500000", "₹15,00,000"
        patterns = [
            r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)\b',  # 15 lakh
            r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:crore|cr)\b',    # 1 crore
            r'(?:₹|rs\.?|inr)?\s*(\d{5,})',                              # Direct amount
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                amount = float(match.group(1))
                if 'crore' in query.lower() or 'cr' in query.lower():
                    return amount * 10000000
                elif 'lakh' in query.lower() or 'lac' in query.lower() or query.lower().endswith('l'):
                    return amount * 100000
                elif amount < 1000:  # Probably in lakhs
                    return amount * 100000
                return amount
        
        return None
    
    def route(self, query: str) -> RouterResult:
        """
        Route query to appropriate handler and return results.
        
        Args:
            query: User's natural language query
        
        Returns:
            RouterResult with handler outputs
        """
        query_type = self.classify(query)
        result = RouterResult(query_type=query_type)
        
        if query_type == QueryType.CALCULATOR:
            result = self._handle_calculator(query, result)
            
        elif query_type == QueryType.RAG:
            result = self._handle_rag(query, result)
            
        elif query_type == QueryType.HYBRID:
            result = self._handle_hybrid(query, result)
            
        return result
    
    def _handle_calculator(self, query: str, result: RouterResult) -> RouterResult:
        """Handle pure calculation queries"""
        income = self.extract_income(query)
        
        if income:
            query_lower = query.lower()
            
            # Check if comparing regimes
            if 'compare' in query_lower or 'which' in query_lower or 'better' in query_lower:
                # Assume some 80C deductions for comparison
                comparison = compare_regimes(income, 150000, 0)
                result.calculator_result = {
                    "type": "comparison",
                    "income": income,
                    "old_tax": comparison.old_regime.total_tax,
                    "new_tax": comparison.new_regime.total_tax,
                    "recommended": comparison.recommended,
                    "savings": comparison.savings
                }
                result.combined_answer = (
                    f"For income of ₹{income:,.0f}:\n"
                    f"• Old Regime Tax: ₹{comparison.old_regime.total_tax:,.0f}\n"
                    f"• New Regime Tax: ₹{comparison.new_regime.total_tax:,.0f}\n"
                    f"• Recommended: {comparison.recommended.upper()} regime "
                    f"(saves ₹{comparison.savings:,.0f})"
                )
            else:
                # Default to new regime calculation
                tax_result = calculate_tax(income, "new")
                result.calculator_result = {
                    "type": "calculation",
                    "income": income,
                    "regime": "new",
                    "taxable_income": tax_result.taxable_income,
                    "total_tax": tax_result.total_tax
                }
                result.combined_answer = (
                    f"For income of ₹{income:,.0f} (New Regime):\n"
                    f"• Taxable Income: ₹{tax_result.taxable_income:,.0f}\n"
                    f"• Tax: ₹{tax_result.total_tax:,.0f}"
                )
            
            result.confidence = 0.9
        else:
            result.combined_answer = "I couldn't determine the income amount. Please specify your income."
            result.confidence = 0.3
        
        return result
    
    def _handle_rag(self, query: str, result: RouterResult) -> RouterResult:
        """Handle knowledge retrieval queries"""
        search_results = self._vector_store.search(query, n_results=3)
        result.rag_results = search_results
        
        if search_results:
            # Combine top results into an answer
            sources = set(r.source for r in search_results)
            top_content = search_results[0].content[:500] if search_results else ""
            
            result.combined_answer = (
                f"Based on {', '.join(sources)}:\n\n{top_content}..."
            )
            result.confidence = search_results[0].score
        else:
            result.combined_answer = "I couldn't find relevant information in the tax knowledge base."
            result.confidence = 0.2
        
        return result
    
    def _handle_hybrid(self, query: str, result: RouterResult) -> RouterResult:
        """Handle queries needing both calculation and context"""
        # First get RAG context
        search_results = self._vector_store.search(query, n_results=2)
        result.rag_results = search_results
        
        # Then try calculation
        income = self.extract_income(query)
        if income:
            comparison = compare_regimes(income, 150000, 0)
            result.calculator_result = {
                "type": "hybrid",
                "income": income,
                "recommended": comparison.recommended,
                "savings": comparison.savings
            }
            
            context = search_results[0].content[:200] if search_results else "No additional context."
            result.combined_answer = (
                f"For ₹{income:,.0f}: {comparison.recommended.upper()} regime saves "
                f"₹{comparison.savings:,.0f}.\n\n"
                f"Context: {context}..."
            )
            result.confidence = 0.8
        else:
            # Fall back to RAG
            result = self._handle_rag(query, result)
        
        return result


# Convenience function
def route_query(query: str) -> RouterResult:
    """Route a query and return results"""
    router = QueryRouter()
    return router.route(query)

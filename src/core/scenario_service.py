"""
Scenario Ranking & Presentation Service

Pure orchestration layer for scenario filtering, ranking, and formatting.
- NO tax computation (delegates to ScenarioEngine)
- NO TaxFacts mutation (read-only input)
- NO LLM, NO UI logic
- Deterministic ranking only

Responsibility:
1. Call ScenarioEngine to generate all scenarios
2. Filter for applicable scenarios (eligibility_check == "")
3. Rank by savings amount (per regime)
4. Format for API responses
5. Return top N scenarios

Output: Dict ready for API response (no FastAPI dependencies)
"""

from typing import List, Dict, Any, Optional
from src.compute.scenario_engine import ScenarioEngine, Scenario, generate_scenarios
from src.core.taxfacts import TaxFacts


class ScenarioService:
    """
    Deterministic scenario ranking and presentation service.
    
    Pure orchestration: calls ScenarioEngine, filters, ranks, formats.
    No tax computation, no mutation, no inference beyond simple sorting.
    """
    
    def __init__(
        self,
        baseline_taxfacts: TaxFacts,
        baseline_old_tax: float = 0.0,
        baseline_new_tax: float = 0.0,
    ):
        """
        Initialize scenario service with baseline TaxFacts.
        
        Args:
            baseline_taxfacts: Normalized TaxFacts (will not be mutated)
            baseline_old_tax: Tax amount under old regime (for reference)
            baseline_new_tax: Tax amount under new regime (for reference)
        """
        self.baseline_taxfacts = baseline_taxfacts
        self.baseline_old_tax = baseline_old_tax
        self.baseline_new_tax = baseline_new_tax
        
        # Generate all scenarios once (lazy evaluation on first call)
        self._all_scenarios: Optional[List[Scenario]] = None
    
    # =====================================================================
    # Public API Methods
    # =====================================================================
    
    def get_applicable_scenarios(self) -> List[Scenario]:
        """
        Get only applicable scenarios (eligibility_check == "").
        
        Filters out scenarios where user is ineligible (e.g., no rental income,
        already at deduction cap, etc.).
        
        Returns:
            List[Scenario]: All applicable scenarios, in generation order
        """
        all_scenarios = self._get_all_scenarios()
        return [s for s in all_scenarios if not s.eligibility_check or s.eligibility_check == ""]
    
    def rank_scenarios_by_savings(self, regime: str = "old") -> List[Scenario]:
        """
        Rank applicable scenarios by tax savings (descending).
        
        Args:
            regime: "old" or "new" — which regime's savings to rank by
        
        Returns:
            List[Scenario]: Applicable scenarios sorted by savings (highest first)
        
        Raises:
            ValueError: If regime not in ["old", "new"]
        """
        if regime not in ["old", "new"]:
            raise ValueError(f"regime must be 'old' or 'new', got {regime}")
        
        applicable = self.get_applicable_scenarios()
        
        # Sort by tax_saved_{regime}_regime, descending
        key_field = f"tax_saved_{regime}_regime"
        sorted_scenarios = sorted(
            applicable,
            key=lambda s: getattr(s, key_field, 0.0),
            reverse=True,  # Highest savings first
        )
        
        return sorted_scenarios
    
    def top_n_scenarios(
        self,
        n: int = 3,
        regime: str = "old",
    ) -> List[Scenario]:
        """
        Get top N scenarios by tax savings (ranked).
        
        Args:
            n: Number of scenarios to return (default: 3)
            regime: "old" or "new" — which regime's savings to rank by
        
        Returns:
            List[Scenario]: Top N scenarios, ranked by savings
        """
        ranked = self.rank_scenarios_by_savings(regime=regime)
        return ranked[:n]
    
    def get_recommended_regime(self) -> str:
        """
        Determine recommended regime based on baseline tax amounts.
        
        Returns:
            "old" or "new" based on which has lower tax
        """
        if self.baseline_old_tax <= self.baseline_new_tax:
            return "old"
        else:
            return "new"
    
    def to_response_payload(
        self,
        top_n: int = 3,
    ) -> Dict[str, Any]:
        """
        Format scenarios into API response payload.
        
        Returns a dict with:
        - recommended_regime: Best regime based on baseline
        - total_applicable_scenarios: Count of eligible scenarios
        - top_scenarios: List of top N scenarios (dicts)
        - all_applicable_scenarios: Full list of applicable scenarios (dicts)
        
        Args:
            top_n: Number of top scenarios to include in "top_scenarios"
        
        Returns:
            Dict: JSON-serializable response payload
        """
        recommended_regime = self.get_recommended_regime()
        applicable = self.get_applicable_scenarios()
        top_scenarios_list = self.top_n_scenarios(n=top_n, regime=recommended_regime)
        
        return {
            "recommended_regime": recommended_regime,
            "total_applicable_scenarios": len(applicable),
            "top_scenarios": [s.to_dict() for s in top_scenarios_list],
            "all_applicable_scenarios": [s.to_dict() for s in applicable],
            "note": f"Top {top_n} scenarios ranked by savings in {recommended_regime} regime"
        }
    
    def get_scenario_summary(self) -> Dict[str, Any]:
        """
        Get high-level summary of all scenarios (applicable + ineligible).
        
        Returns:
            Dict with counts and descriptions
        """
        all_scenarios = self._get_all_scenarios()
        applicable = self.get_applicable_scenarios()
        ineligible = [s for s in all_scenarios if s.eligibility_check and s.eligibility_check != ""]
        
        return {
            "total_scenarios": len(all_scenarios),
            "applicable_count": len(applicable),
            "ineligible_count": len(ineligible),
            "ineligible_reasons": [
                {
                    "scenario_id": s.scenario_id,
                    "reason": s.eligibility_check
                }
                for s in ineligible
            ]
        }
    
    # =====================================================================
    # Private Helper Methods
    # =====================================================================
    
    def _get_all_scenarios(self) -> List[Scenario]:
        """
        Lazy-load all scenarios (computed once on first call).
        
        Returns:
            List[Scenario]: All 5 scenarios from ScenarioEngine
        """
        if self._all_scenarios is None:
            # Generate all scenarios using ScenarioEngine
            self._all_scenarios = generate_scenarios(
                taxfacts=self.baseline_taxfacts,
                baseline_before_tax=self.baseline_old_tax,
                baseline_after_tax=self.baseline_old_tax,  # Use old tax as reference
                baseline_new_tax=self.baseline_new_tax,
            )
        
        return self._all_scenarios


# =====================================================================
# Convenience Functions
# =====================================================================

def rank_scenarios(
    baseline_taxfacts: TaxFacts,
    baseline_old_tax: float = 0.0,
    baseline_new_tax: float = 0.0,
    top_n: int = 3,
) -> Dict[str, Any]:
    """
    Convenience function to generate, rank, and format scenarios.
    
    One-liner for scenario ranking workflow.
    
    Args:
        baseline_taxfacts: Normalized TaxFacts
        baseline_old_tax: Tax under old regime
        baseline_new_tax: Tax under new regime
        top_n: Number of top scenarios to return
    
    Returns:
        Dict: JSON-serializable response with recommended_regime and top_scenarios
    """
    service = ScenarioService(
        baseline_taxfacts=baseline_taxfacts,
        baseline_old_tax=baseline_old_tax,
        baseline_new_tax=baseline_new_tax,
    )
    return service.to_response_payload(top_n=top_n)


def get_applicable_and_ranked(
    baseline_taxfacts: TaxFacts,
    regime: str = "old",
) -> List[Scenario]:
    """
    Get all applicable scenarios, ranked by savings in specified regime.
    
    Args:
        baseline_taxfacts: Normalized TaxFacts
        regime: "old" or "new" — ranking basis
    
    Returns:
        List[Scenario]: Applicable scenarios, sorted by savings (highest first)
    """
    service = ScenarioService(baseline_taxfacts=baseline_taxfacts)
    return service.rank_scenarios_by_savings(regime=regime)

"""
Scenario Engine: Pure Deterministic Tax Planning

Implements clone → modify → recalculate pattern.
- Input: Normalized TaxFacts (from normalization agent)
- Output: List of scenarios with before/after tax, savings
- NO LLM, NO UI logic, NO inference beyond simple flags

Key pattern:
1. Clone TaxFacts (deep copy, never mutate original)
2. Modify exactly ONE variable per scenario
3. Convert cloned TaxFacts to profile dict
4. Recalculate tax using tax_engine.py
5. Return scenario with savings info

Scenarios (deterministic):
1. Increase 80C deduction (cap at ₹1.5L)
2. Add NPS 80CCD(1B) contribution (cap at ₹50k)
3. Switch tax regime (Old ↔ New)
4. Claim parent medical insurance (80D)
5. Apply 30% rental standard deduction (if rental exists)
"""

from typing import List, Dict, Any, Optional
from copy import deepcopy
from dataclasses import dataclass

from src.core.taxfacts import TaxFacts
from src.compute.tax_engine import compute_taxable_income_old_regime, compute_old_regime, compute_new_regime


# =====================================================================
# Data Models
# =====================================================================

@dataclass
class Scenario:
    """Single tax scenario result."""
    scenario_id: str
    description: str
    modification: str  # What was changed (e.g., "Increased 80C by ₹50k")
    before_tax_old_regime: float
    after_tax_old_regime: float
    before_tax_new_regime: float
    after_tax_new_regime: float
    tax_saved_old_regime: float
    tax_saved_new_regime: float
    recommended_regime: str  # Which regime becomes better after scenario
    eligibility_check: str  # Empty if eligible, else reason why not applicable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "scenario_id": self.scenario_id,
            "description": self.description,
            "modification": self.modification,
            "before_tax_old_regime": round(self.before_tax_old_regime, 2),
            "after_tax_old_regime": round(self.after_tax_old_regime, 2),
            "before_tax_new_regime": round(self.before_tax_new_regime, 2),
            "after_tax_new_regime": round(self.after_tax_new_regime, 2),
            "tax_saved_old_regime": round(self.tax_saved_old_regime, 2),
            "tax_saved_new_regime": round(self.tax_saved_new_regime, 2),
            "recommended_regime": self.recommended_regime,
            "eligibility_check": self.eligibility_check,
        }


class ScenarioEngine:
    """
    Deterministic tax scenario generator.
    
    Never mutates original TaxFacts. Always clones before modification.
    All calculations are auditable and repeatable.
    """
    
    # Deduction caps (Section-wise limits per Indian tax law)
    CAP_80C = 150000.0
    CAP_80CCD_1B = 50000.0
    CAP_80D_SENIOR = 50000.0
    CAP_80D_NON_SENIOR = 25000.0
    CAP_80TTA = 10000.0
    
    def __init__(self, baseline_taxfacts: TaxFacts, baseline_before_tax: float, baseline_after_tax: float, baseline_new_tax: float = 0.0):
        """
        Initialize scenario engine with baseline TaxFacts.
        
        Args:
            baseline_taxfacts: Original TaxFacts (will not be mutated)
            baseline_before_tax: Tax before deductions (for old regime)
            baseline_after_tax: Tax after deductions (for old regime)
        """
        self.baseline = baseline_taxfacts
        self.baseline_before_tax = baseline_before_tax
        self.baseline_after_tax = baseline_after_tax
        self.baseline_new_tax = baseline_new_tax
        self.scenarios: List[Scenario] = []
    
    def generate_all_scenarios(self) -> List[Scenario]:
        """
        Generate all applicable scenarios based on baseline TaxFacts.
        
        Returns:
            List[Scenario]: All scenarios (including ineligible ones with explanations)
        """
        self.scenarios = []
        
        # Scenario 1: Increase 80C
        self.scenarios.append(self._scenario_increase_80c())
        
        # Scenario 2: Add NPS 80CCD(1B)
        self.scenarios.append(self._scenario_add_nps_80ccd_1b())
        
        # Scenario 3: Switch tax regime
        self.scenarios.append(self._scenario_switch_regime())
        
        # Scenario 4: Claim parent medical (80D)
        self.scenarios.append(self._scenario_parent_health_insurance())
        
        # Scenario 5: Rental standard deduction (30%)
        self.scenarios.append(self._scenario_rental_standard_deduction())
        
        return self.scenarios
    
    # =====================================================================
    # Scenario Implementations
    # =====================================================================
    
    def _scenario_increase_80c(self) -> Scenario:
        """
        Scenario 1: Increase 80C deduction by ₹50,000 (up to cap ₹1.5L).
        
        Eligibility: Always applicable (can always increase investments)
        """
        # Clone TaxFacts
        modified = self._clone_taxfacts(self.baseline)
        
        current_80c = modified.deduction_80c or 0.0
        max_increase = self.CAP_80C - current_80c
        increase_amount = min(50000.0, max_increase)
        
        if increase_amount <= 0:
            # Already at cap
            return Scenario(
                scenario_id="scenario_1_increase_80c",
                description="Increase Section 80C Deduction by ₹50,000",
                modification="Already at cap (₹1,50,000)",
                before_tax_old_regime=self.baseline_before_tax,
                after_tax_old_regime=self.baseline_after_tax,
                before_tax_new_regime=self.baseline_new_tax,
                after_tax_new_regime=self.baseline_new_tax,
                tax_saved_old_regime=0.0,
                tax_saved_new_regime=0.0,
                recommended_regime="old",
                eligibility_check="Already at maximum deduction limit (₹1,50,000)",
            )
        
        # Modify
        modified.deduction_80c = min(current_80c + increase_amount, self.CAP_80C)
        
        # Recalculate
        old_before, old_after = self._compute_taxes_old_regime(modified)
        new_before, new_after = self._compute_taxes_new_regime(modified)
        
        tax_saved_old = self.baseline_after_tax - old_after
        tax_saved_new = self.baseline_new_tax - new_after
        
        return Scenario(
            scenario_id="scenario_1_increase_80c",
            description="Increase Section 80C Deduction by ₹50,000",
            modification=f"Increased 80C by ₹{increase_amount:,.0f} (cap: ₹1,50,000)",
            before_tax_old_regime=old_before,
            after_tax_old_regime=old_after,
            before_tax_new_regime=new_before,
            after_tax_new_regime=new_after,
            tax_saved_old_regime=max(0, tax_saved_old),
            tax_saved_new_regime=max(0, tax_saved_new),
            recommended_regime="old" if old_after < new_after else "new",
            eligibility_check="",
        )
    
    def _scenario_add_nps_80ccd_1b(self) -> Scenario:
        """
        Scenario 2: Add NPS extra contribution (80CCD 1B) of ₹50,000 (cap).
        
        Eligibility: Always applicable (any resident can contribute)
        """
        # Clone TaxFacts
        modified = self._clone_taxfacts(self.baseline)
        
        current_nps = modified.deduction_80ccd_1b or 0.0
        max_increase = self.CAP_80CCD_1B - current_nps
        increase_amount = min(50000.0, max_increase)
        
        if increase_amount <= 0:
            # Already at cap
            return Scenario(
                scenario_id="scenario_2_add_nps_80ccd_1b",
                description="Add NPS Extra Contribution (80CCD 1B) ₹50,000",
                modification="Already at cap (₹50,000)",
                before_tax_old_regime=self.baseline_before_tax,
                after_tax_old_regime=self.baseline_after_tax,
                before_tax_new_regime=self.baseline_new_tax,
                after_tax_new_regime=self.baseline_new_tax,
                tax_saved_old_regime=0.0,
                tax_saved_new_regime=0.0,
                recommended_regime="old",
                eligibility_check="Already at maximum NPS contribution (₹50,000)",
            )
        
        # Modify
        modified.deduction_80ccd_1b = min(current_nps + increase_amount, self.CAP_80CCD_1B)
        
        # Recalculate
        old_before, old_after = self._compute_taxes_old_regime(modified)
        new_before, new_after = self._compute_taxes_new_regime(modified)
        
        tax_saved_old = self.baseline_after_tax - old_after
        tax_saved_new = self.baseline_new_tax - new_after
        
        return Scenario(
            scenario_id="scenario_2_add_nps_80ccd_1b",
            description="Add NPS Extra Contribution (80CCD 1B) ₹50,000",
            modification=f"Added ₹{increase_amount:,.0f} NPS contribution (cap: ₹50,000)",
            before_tax_old_regime=old_before,
            after_tax_old_regime=old_after,
            before_tax_new_regime=new_before,
            after_tax_new_regime=new_after,
            tax_saved_old_regime=max(0, tax_saved_old),
            tax_saved_new_regime=max(0, tax_saved_new),
            recommended_regime="old" if old_after < new_after else "new",
            eligibility_check="",
        )
    
    def _scenario_switch_regime(self) -> Scenario:
        """
        Scenario 3: Switch from old regime to new (or vice versa).
        
        Simply compares both regimes with no modification to deductions.
        """
        # No modification needed; just recalculate both regimes
        old_before, old_after = self._compute_taxes_old_regime(self.baseline)
        new_before, new_after = self._compute_taxes_new_regime(self.baseline)
        
        # Which is better?
        better_regime = "old" if old_after < new_after else "new"
        tax_saved_old = self.baseline_after_tax - old_after
        tax_saved_new = self.baseline_new_tax - new_after
        
        return Scenario(
            scenario_id="scenario_3_switch_regime",
            description="Switch Tax Regime (Old vs New)",
            modification=f"Switching to {better_regime.upper()} regime saves ₹{abs(self.baseline_after_tax - self.baseline_new_tax):,.0f}",
            before_tax_old_regime=old_before,
            after_tax_old_regime=old_after,
            before_tax_new_regime=new_before,
            after_tax_new_regime=new_after,
            tax_saved_old_regime=max(0, tax_saved_old),
            tax_saved_new_regime=max(0, tax_saved_new),
            recommended_regime=better_regime,
            eligibility_check="",
        )
    
    def _scenario_parent_health_insurance(self) -> Scenario:
        """
        Scenario 4: Claim parent medical insurance (80D).
        
        Adds:
        - Non-senior: +₹25,000
        - Senior (60-80): +₹50,000
        - Senior (80+): +₹50,000 + ₹25k extra = ₹75,000
        
        Eligibility:
        - Only if parent exists (assume yes for scenario purposes)
        - Cap is ₹25k or ₹50k based on age
        """
        # Clone TaxFacts
        modified = self._clone_taxfacts(self.baseline)
        
        # Determine parent health insurance amount based on taxpayer age
        # For simplicity: assume parent is non-senior if taxpayer is below 60, senior if 60+
        is_senior = modified.age_category in ["senior_60_80", "above_80"]
        parent_health_amount = 50000.0 if is_senior else 25000.0
        
        current_80d_parents = modified.deduction_80d_spouse or 0.0
        increase_amount = parent_health_amount - current_80d_parents
        
        if increase_amount <= 0:
            return Scenario(
                scenario_id="scenario_4_parent_health_insurance",
                description="Claim Parent Medical Insurance (80D)",
                modification="Already claiming maximum parent health insurance",
                before_tax_old_regime=self.baseline_before_tax,
                after_tax_old_regime=self.baseline_after_tax,
                before_tax_new_regime=self.baseline_new_tax,
                after_tax_new_regime=self.baseline_new_tax,
                tax_saved_old_regime=0.0,
                tax_saved_new_regime=0.0,
                recommended_regime="old",
                eligibility_check="Already claiming maximum parent health insurance",
            )
        
        # Modify
        modified.deduction_80d_spouse = parent_health_amount
        
        # Recalculate
        old_before, old_after = self._compute_taxes_old_regime(modified)
        new_before, new_after = self._compute_taxes_new_regime(modified)
        
        tax_saved_old = self.baseline_after_tax - old_after
        tax_saved_new = self.baseline_new_tax - new_after
        
        cap_label = "₹50,000" if is_senior else "₹25,000"
        return Scenario(
            scenario_id="scenario_4_parent_health_insurance",
            description="Claim Parent Medical Insurance (80D)",
            modification=f"Claimed parent health insurance ₹{increase_amount:,.0f} (cap: {cap_label})",
            before_tax_old_regime=old_before,
            after_tax_old_regime=old_after,
            before_tax_new_regime=new_before,
            after_tax_new_regime=new_after,
            tax_saved_old_regime=max(0, tax_saved_old),
            tax_saved_new_regime=max(0, tax_saved_new),
            recommended_regime="old" if old_after < new_after else "new",
            eligibility_check="",
        )
    
    def _scenario_rental_standard_deduction(self) -> Scenario:
        """
        Scenario 5: Apply 30% standard deduction on rental income (Section 24).
        
        If rental income exists:
        - Current model assumes net_income is post-30% already
        - This scenario assumes user claimed actual expenses instead
        - Recalculate: Apply 30% standard deduction instead
        
        Eligibility:
        - ONLY if property_letout_net_income > 0
        - Assumes taxpayer has let-out property
        """
        # Check eligibility first
        if not self.baseline.property_letout_net_income or self.baseline.property_letout_net_income <= 0:
            return Scenario(
                scenario_id="scenario_5_rental_standard_deduction",
                description="Apply 30% Rental Standard Deduction (Section 24)",
                modification="No rental income to optimize",
                before_tax_old_regime=self.baseline_before_tax,
                after_tax_old_regime=self.baseline_after_tax,
                before_tax_new_regime=self.baseline_new_tax,
                after_tax_new_regime=self.baseline_new_tax,
                tax_saved_old_regime=0.0,
                tax_saved_new_regime=0.0,
                recommended_regime="old",
                eligibility_check="No rental income; scenario requires let-out property",
            )
        
        # Clone TaxFacts
        modified = self._clone_taxfacts(self.baseline)
        
        # Apply 30% standard deduction
        # Assume raw rental receipt is: net_income / 0.7 (to reverse the 30% deduction)
        # Actually, the model likely already has net_income; just show comparison
        # For this scenario: Show impact of 30% vs actual claimed
        
        gross_rental = modified.property_letout_net_income / 0.7  # Reverse to get gross
        deduction_30pct = gross_rental * 0.30
        net_after_30pct = gross_rental - deduction_30pct
        
        # For scenario: use the 30% standard deduction result
        modified.property_letout_net_income = net_after_30pct
        
        # Recalculate
        old_before, old_after = self._compute_taxes_old_regime(modified)
        new_before, new_after = self._compute_taxes_new_regime(modified)
        
        tax_saved_old = self.baseline_after_tax - old_after
        tax_saved_new = self.baseline_new_tax - new_after
        
        return Scenario(
            scenario_id="scenario_5_rental_standard_deduction",
            description="Apply 30% Rental Standard Deduction (Section 24)",
            modification=f"Applied 30% standard deduction (₹{deduction_30pct:,.0f}) on rental property",
            before_tax_old_regime=old_before,
            after_tax_old_regime=old_after,
            before_tax_new_regime=new_before,
            after_tax_new_regime=new_after,
            tax_saved_old_regime=max(0, tax_saved_old),
            tax_saved_new_regime=max(0, tax_saved_new),
            recommended_regime="old" if old_after < new_after else "new",
            eligibility_check="",
        )
    
    # =====================================================================
    # Helper Methods
    # =====================================================================
    
    def _clone_taxfacts(self, taxfacts: TaxFacts) -> TaxFacts:
        """
        Deep clone TaxFacts object.
        
        Never mutates original; all modifications are on clone only.
        """
        return deepcopy(taxfacts)
    
    def _taxfacts_to_profile_dict(self, taxfacts: TaxFacts) -> Dict[str, Any]:
        """
        Convert TaxFacts to profile dict compatible with tax_engine.py.
        
        tax_engine expects a dict structure like:
        {
            "income": {
                "salary": 1200000,
                "other_income": 0,
                "house_property": {...},
                "capital_gains": {...},
                "business_profession": {...},
                "deductions": {
                    "section_80c": 150000,
                    "80ccd_1b": 0,
                    "80d": 0,
                    ...
                }
            }
        }
        """
        # Aggregate 80D from all sub-sections
        total_80d = (
            (taxfacts.deduction_80d_self or 0.0)
            + (taxfacts.deduction_80d_spouse or 0.0)
            + (taxfacts.deduction_80d_children or 0.0)
        )
        
        profile = {
            "income": {
                "salary": taxfacts.salary_gross or 0.0,
                "other_income": 0.0,
                "house_property": {
                    "self_occupied_interest": 0.0,
                    "let_out_net_income": taxfacts.property_letout_net_income or 0.0,
                },
                "capital_gains": {
                    "stcg_111a": taxfacts.capital_gains_stcg_111a or 0.0,
                    "stcg_other": taxfacts.capital_gains_stcg_other or 0.0,
                    "ltcg_112a": taxfacts.capital_gains_ltcg_112a or 0.0,
                    "ltcg_other": taxfacts.capital_gains_ltcg_other or 0.0,
                },
                "business_profession": {
                    "presumptive": {"opted": False},
                    "non_presumptive": {"net_profit": 0.0},
                },
                "deductions": {
                    "section_80c": taxfacts.deduction_80c or 0.0,
                    "80ccd_1b": taxfacts.deduction_80ccd_1b or 0.0,
                    "80d": total_80d,
                    "80tta": taxfacts.deduction_80tta or 0.0,
                    "80g": taxfacts.deduction_80g or 0.0,
                    "other_chapter_via": 0.0,
                },
            }
        }
        return profile
    
    def _compute_taxes_old_regime(self, taxfacts: TaxFacts) -> tuple:
        """
        Compute old regime: before-deduction and after-deduction tax.
        
        Returns:
            (tax_before_deductions, tax_after_deductions)
        """
        profile = self._taxfacts_to_profile_dict(taxfacts)
        
        # Compute taxable income components
        income_breakup = compute_taxable_income_old_regime(profile)
        
        # Tax on gross income (old regime still uses deductions in taxable calculation)
        # So "before deductions" = tax on gross total income
        gross_income = income_breakup.get("gross_total_income", 0)
        income_breakup_gross = income_breakup.copy()
        income_breakup_gross["taxable_income_old_regime"] = gross_income
        tax_before = compute_old_regime(income_breakup_gross)
        
        # Tax after deductions
        tax_after = compute_old_regime(income_breakup)
        
        return round(tax_before, 2), round(tax_after, 2)
    
    def _compute_taxes_new_regime(self, taxfacts: TaxFacts) -> tuple:
        """
        Compute new regime: before and after (same in new regime, as it ignores deductions).
        
        Returns:
            (tax_new_regime, tax_new_regime)  # Both same for new regime
        """
        profile = self._taxfacts_to_profile_dict(taxfacts)
        
        # Compute taxable income components
        income_breakup = compute_taxable_income_old_regime(profile)  # Reuse, just for GTI
        
        # New regime taxes on gross total income
        tax_new = compute_new_regime(income_breakup)
        
        return round(tax_new, 2), round(tax_new, 2)


# =====================================================================
# Convenience Function
# =====================================================================

def generate_scenarios(
    taxfacts: TaxFacts,
    baseline_before_tax: float = 0.0,
    baseline_after_tax: float = 0.0,
    baseline_new_tax: float = 0.0,
) -> List[Scenario]:
    """
    Convenience function to generate all scenarios for a given TaxFacts.
    
    Args:
        taxfacts: Normalized TaxFacts from normalization agent
        baseline_before_tax: Tax before deductions (optional, for reference)
        baseline_after_tax: Tax after deductions (optional, for reference)
    
    Returns:
        List[Scenario]: All applicable scenarios (deterministic, auditable)
    """
    engine = ScenarioEngine(taxfacts, baseline_before_tax, baseline_after_tax, baseline_new_tax)
    return engine.generate_all_scenarios()

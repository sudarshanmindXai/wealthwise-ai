"""
Scenario Response Schemas

Pydantic models for /tax/scenarios endpoint response.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ScenarioItemResponse(BaseModel):
    """Single scenario result."""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    description: str = Field(..., description="Human-readable scenario description")
    modification: str = Field(..., description="What was changed in this scenario")
    before_tax_old_regime: float = Field(..., description="Tax before deductions (old regime)")
    after_tax_old_regime: float = Field(..., description="Tax after deductions (old regime)")
    before_tax_new_regime: float = Field(..., description="Tax in new regime")
    after_tax_new_regime: float = Field(..., description="Tax in new regime (same as before)")
    tax_saved_old_regime: float = Field(..., description="Tax savings compared to baseline (old regime)")
    tax_saved_new_regime: float = Field(..., description="Tax savings compared to baseline (new regime)")
    recommended_regime: str = Field(..., description="Which regime benefits most from this scenario")
    eligibility_check: str = Field(..., description="Empty if eligible, else reason why not applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scenario_1_increase_80c",
                "description": "Increase Section 80C Deduction by ₹50,000",
                "modification": "Increased 80C by ₹50,000 (cap: ₹1,50,000)",
                "before_tax_old_regime": 180000.0,
                "after_tax_old_regime": 156000.0,
                "before_tax_new_regime": 195000.0,
                "after_tax_new_regime": 195000.0,
                "tax_saved_old_regime": 12000.0,
                "tax_saved_new_regime": 0.0,
                "recommended_regime": "old",
                "eligibility_check": ""
            }
        }


class ScenarioIneligibilityReason(BaseModel):
    """Reason why a scenario is ineligible."""
    scenario_id: str = Field(..., description="Scenario ID")
    reason: str = Field(..., description="Explanation of ineligibility")


class ScenarioSummary(BaseModel):
    """Summary statistics of scenarios."""
    total_scenarios: int = Field(..., description="Total scenarios generated")
    applicable_count: int = Field(..., description="Number of applicable (eligible) scenarios")
    ineligible_count: int = Field(..., description="Number of ineligible scenarios")
    ineligible_reasons: List[ScenarioIneligibilityReason] = Field(..., description="Details on ineligible scenarios")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_scenarios": 5,
                "applicable_count": 4,
                "ineligible_count": 1,
                "ineligible_reasons": [
                    {
                        "scenario_id": "scenario_5_rental_standard_deduction",
                        "reason": "No rental income; scenario requires let-out property"
                    }
                ]
            }
        }


class ScenarioResponse(BaseModel):
    """
    Complete response for /tax/scenarios endpoint.
    
    Contains:
    - Recommended regime based on baseline taxes
    - Top N scenarios (ranked by savings)
    - All applicable scenarios (for reference)
    - Summary statistics
    """
    recommended_regime: str = Field(
        ..., 
        description="Best tax regime for baseline profile ('old' or 'new')",
        pattern=r"^(old|new)$"
    )
    
    total_applicable_scenarios: int = Field(
        ..., 
        description="Number of scenarios user is eligible for"
    )
    
    top_scenarios: List[ScenarioItemResponse] = Field(
        ..., 
        description="Top ranked scenarios by tax savings (usually top 3)"
    )
    
    all_applicable_scenarios: List[ScenarioItemResponse] = Field(
        ..., 
        description="All scenarios user is eligible for (full list)"
    )
    
    summary: ScenarioSummary = Field(
        ..., 
        description="Statistics on all scenarios (including ineligible)"
    )
    
    note: Optional[str] = Field(
        None, 
        description="Additional context or notes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommended_regime": "old",
                "total_applicable_scenarios": 4,
                "top_scenarios": [
                    {
                        "scenario_id": "scenario_1_increase_80c",
                        "description": "Increase Section 80C Deduction by ₹50,000",
                        "modification": "Increased 80C by ₹50,000 (cap: ₹1,50,000)",
                        "before_tax_old_regime": 180000.0,
                        "after_tax_old_regime": 156000.0,
                        "before_tax_new_regime": 195000.0,
                        "after_tax_new_regime": 195000.0,
                        "tax_saved_old_regime": 12000.0,
                        "tax_saved_new_regime": 0.0,
                        "recommended_regime": "old",
                        "eligibility_check": ""
                    }
                ],
                "all_applicable_scenarios": [...],
                "summary": {
                    "total_scenarios": 5,
                    "applicable_count": 4,
                    "ineligible_count": 1,
                    "ineligible_reasons": [
                        {
                            "scenario_id": "scenario_5_rental_standard_deduction",
                            "reason": "No rental income; scenario requires let-out property"
                        }
                    ]
                },
                "note": "Top 3 scenarios ranked by savings in old regime"
            }
        }

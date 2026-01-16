"""
WealthWise AI - Chat Tools
===========================
Functions the LLM can call during conversation.
"""

from typing import Optional
from dataclasses import dataclass

# Import calculator for "What If" scenarios
from ..engine.calculator import calculate_tax, compare_regimes
from ..engine.constants import (
    METRO_CITIES,
    MAX_80CCD_2_RATE,
    HRA_METRO_RATE,
    HRA_NON_METRO_RATE,
)


@dataclass
class ToolResult:
    """Result from a tool call"""
    success: bool
    data: dict
    message: str


def recalculate_tax(
    gross_salary: float,
    rent_monthly: float = 0,
    employer_nps: float = 0,
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    is_metro: bool = True,
    basic_salary: Optional[float] = None,
) -> ToolResult:
    """
    Recalculate tax with hypothetical values.
    Used for "What If" scenarios.
    
    Args:
        gross_salary: Annual gross salary
        rent_monthly: Monthly rent (for HRA calculation)
        employer_nps: Employer NPS contribution (80CCD2)
        deductions_80c: Total 80C deductions
        deductions_80d: Health insurance (80D)
        is_metro: Whether living in metro city
        basic_salary: Basic salary (defaults to 50% of gross)
    """
    try:
        # Estimate basic if not provided
        if basic_salary is None:
            basic_salary = gross_salary * 0.50
        
        # Calculate HRA exemption
        rent_annual = rent_monthly * 12
        hra_rate = HRA_METRO_RATE if is_metro else HRA_NON_METRO_RATE
        hra_exemption = min(
            gross_salary * 0.20,  # Assume HRA = 20% of gross
            max(0, rent_annual - 0.10 * basic_salary),
            basic_salary * hra_rate,
        )
        
        # Calculate NPS deduction
        max_nps = basic_salary * MAX_80CCD_2_RATE
        nps_deduction = min(employer_nps, max_nps)
        
        # Total deductions for old regime
        total_deductions = (
            deductions_80c +
            deductions_80d +
            nps_deduction +
            hra_exemption
        )
        
        # Compare regimes
        comparison = compare_regimes(
            gross_income=gross_salary,
            deductions=total_deductions,
        )
        
        return ToolResult(
            success=True,
            data={
                "old_regime": {
                    "taxable_income": comparison.old_regime.taxable_income,
                    "tax_payable": comparison.old_regime.total_tax,
                },
                "new_regime": {
                    "taxable_income": comparison.new_regime.taxable_income,
                    "tax_payable": comparison.new_regime.total_tax,
                },
                "recommended": comparison.recommended,
                "savings": comparison.savings,
                "deductions_applied": {
                    "hra_exemption": hra_exemption,
                    "nps_80ccd2": nps_deduction,
                    "section_80c": deductions_80c,
                    "section_80d": deductions_80d,
                    "total": total_deductions,
                },
            },
            message=f"With these changes, {comparison.recommended.upper()} regime saves ₹{comparison.savings:,.0f}",
        )
    
    except Exception as e:
        return ToolResult(
            success=False,
            data={},
            message=f"Calculation error: {str(e)}",
        )


def calculate_hra_exemption(
    basic_salary: float,
    hra_received: float,
    rent_paid_monthly: float,
    is_metro: bool = True,
) -> ToolResult:
    """
    Calculate HRA exemption under Section 10(13A).
    
    Returns breakdown of the three components and final exemption.
    """
    try:
        rent_annual = rent_paid_monthly * 12
        rate = HRA_METRO_RATE if is_metro else HRA_NON_METRO_RATE
        
        component_1 = hra_received  # Actual HRA
        component_2 = max(0, rent_annual - 0.10 * basic_salary)  # Rent - 10% Basic
        component_3 = basic_salary * rate  # 50% or 40% of Basic
        
        exemption = min(component_1, component_2, component_3)
        limiting_factor = "Actual HRA"
        if exemption == component_2:
            limiting_factor = "Rent - 10% Basic"
        elif exemption == component_3:
            limiting_factor = f"{int(rate*100)}% of Basic"
        
        return ToolResult(
            success=True,
            data={
                "actual_hra": component_1,
                "rent_minus_10pct_basic": component_2,
                "percentage_of_basic": component_3,
                "exemption": exemption,
                "limiting_factor": limiting_factor,
            },
            message=f"HRA Exemption: ₹{exemption:,.0f} (limited by {limiting_factor})",
        )
    
    except Exception as e:
        return ToolResult(
            success=False,
            data={},
            message=f"Calculation error: {str(e)}",
        )


def search_tax_law(query: str) -> ToolResult:
    """
    Search the legal knowledge base for relevant sections.
    Uses RAG to find matching content.
    """
    try:
        # Import vector store
        from ..engine.vector_store import VectorStore
        
        store = VectorStore()
        results = store.search(query, n_results=3)
        
        if not results:
            return ToolResult(
                success=True,
                data={"results": []},
                message="No matching sections found. Please try a different query.",
            )
        
        formatted = []
        for r in results:
            formatted.append({
                "section": r.get("metadata", {}).get("section", "Unknown"),
                "doc_type": r.get("metadata", {}).get("doc_type", "Unknown"),
                "text": r.get("text", "")[:500],  # Limit text length
            })
        
        return ToolResult(
            success=True,
            data={"results": formatted},
            message=f"Found {len(formatted)} relevant sections.",
        )
    
    except Exception as e:
        return ToolResult(
            success=False,
            data={"results": []},
            message=f"Search error: {str(e)}",
        )


# Tool definitions for LLM function calling
TOOL_DEFINITIONS = [
    {
        "name": "recalculate_tax",
        "description": "Calculate tax with hypothetical values. Use when user asks 'What if I pay more rent?' or 'What if I add NPS?'",
        "parameters": {
            "type": "object",
            "properties": {
                "gross_salary": {"type": "number", "description": "Annual gross salary"},
                "rent_monthly": {"type": "number", "description": "Monthly rent paid"},
                "employer_nps": {"type": "number", "description": "Employer NPS contribution"},
                "deductions_80c": {"type": "number", "description": "Section 80C deductions"},
                "is_metro": {"type": "boolean", "description": "Living in metro city"},
            },
            "required": ["gross_salary"],
        },
    },
    {
        "name": "calculate_hra_exemption",
        "description": "Calculate HRA exemption breakdown. Use when user asks about HRA calculation.",
        "parameters": {
            "type": "object",
            "properties": {
                "basic_salary": {"type": "number", "description": "Annual basic salary"},
                "hra_received": {"type": "number", "description": "Annual HRA received"},
                "rent_paid_monthly": {"type": "number", "description": "Monthly rent paid"},
                "is_metro": {"type": "boolean", "description": "Living in metro city"},
            },
            "required": ["basic_salary", "hra_received", "rent_paid_monthly"],
        },
    },
    {
        "name": "search_tax_law",
        "description": "Search Income Tax Act for specific sections or rules. Use when user asks about specific legal provisions.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for tax law"},
            },
            "required": ["query"],
        },
    },
]


# Export
__all__ = [
    "recalculate_tax",
    "calculate_hra_exemption",
    "search_tax_law",
    "TOOL_DEFINITIONS",
    "ToolResult",
]

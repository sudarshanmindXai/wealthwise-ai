"""
WealthWise AI - Calculator Endpoint
====================================
Endpoints for tax calculation and regime comparison.
"""

from fastapi import APIRouter, HTTPException

from ...models.schemas import (
    RegimeCompareRequest,
    RegimeCompareResponse,
    TaxBreakdownResponse,
)
from ...engine.calculator import calculate_tax, compare_regimes


router = APIRouter()


@router.post("/calculate")
async def calculate_tax_endpoint(
    income: float,
    regime: str = "new",
    deductions: float = 0,
):
    """
    Calculate tax for given income and regime.
    """
    try:
        result = calculate_tax(
            gross_income=income,
            regime=regime,
            deductions=deductions,
        )
        
        return TaxBreakdownResponse(
            regime=result.regime,
            gross_income=result.gross_income,
            standard_deduction=result.standard_deduction,
            deductions=result.deductions,
            taxable_income=result.taxable_income,
            tax_on_slabs=result.tax_on_slabs,
            rebate_87a=result.rebate_87a,
            tax_after_rebate=result.tax_after_rebate,
            surcharge=result.surcharge,
            cess=result.cess,
            total_tax=result.total_tax,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regime-compare", response_model=RegimeCompareResponse)
async def compare_regimes_endpoint(request: RegimeCompareRequest):
    """
    Compare Old vs New tax regime and recommend optimal choice.
    """
    try:
        result = compare_regimes(
            gross_income=request.gross_income,
            deductions=request.deductions,
        )
        
        return RegimeCompareResponse(
            old_regime=TaxBreakdownResponse(
                regime=result.old_regime.regime,
                gross_income=result.old_regime.gross_income,
                standard_deduction=result.old_regime.standard_deduction,
                deductions=result.old_regime.deductions,
                taxable_income=result.old_regime.taxable_income,
                tax_on_slabs=result.old_regime.tax_on_slabs,
                rebate_87a=result.old_regime.rebate_87a,
                tax_after_rebate=result.old_regime.tax_after_rebate,
                surcharge=result.old_regime.surcharge,
                cess=result.old_regime.cess,
                total_tax=result.old_regime.total_tax,
            ),
            new_regime=TaxBreakdownResponse(
                regime=result.new_regime.regime,
                gross_income=result.new_regime.gross_income,
                standard_deduction=result.new_regime.standard_deduction,
                deductions=result.new_regime.deductions,
                taxable_income=result.new_regime.taxable_income,
                tax_on_slabs=result.new_regime.tax_on_slabs,
                rebate_87a=result.new_regime.rebate_87a,
                tax_after_rebate=result.new_regime.tax_after_rebate,
                surcharge=result.new_regime.surcharge,
                cess=result.new_regime.cess,
                total_tax=result.new_regime.total_tax,
            ),
            recommended=result.recommended,
            savings=result.savings,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

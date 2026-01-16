"""
WealthWise AI - Audit Endpoint
===============================
Main endpoint for running Guardian analysis.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from ...models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    GuardianResultResponse,
    FindingResponse,
)
from ...guardians import run_audit, GuardianType


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_profile(request: AnalyzeRequest):
    """
    Run the 4 Guardians analysis on user financial profile.
    
    Returns optimization findings and potential savings.
    """
    try:
        # Convert request to dict format expected by guardians
        data = _prepare_guardian_data(request)
        
        # Run audit
        result = run_audit(data)
        
        # Convert to response format
        guardians_response = {}
        for gt, gr in result.results.items():
            findings = [
                FindingResponse(
                    guardian=f.guardian.value,
                    severity=f.severity.value,
                    category=f.category.value,
                    title=f.title,
                    description=f.description,
                    potential_savings=f.potential_savings,
                    action_required=f.action_required,
                    action_steps=f.action_steps,
                    related_section=f.related_section,
                )
                for f in gr.findings
            ]
            
            guardians_response[gt.value] = GuardianResultResponse(
                guardian=gt.value,
                taxable_contribution=gr.taxable_income_contribution,
                findings=findings,
                metadata=gr.metadata,
            )
        
        return AnalyzeResponse(
            total_taxable_income=result.total_taxable_income,
            total_potential_savings=result.total_potential_savings,
            has_critical_findings=result.has_critical_findings,
            finding_counts=result.finding_count,
            guardians=guardians_response,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _prepare_guardian_data(request: AnalyzeRequest) -> dict:
    """Convert API request to guardian-compatible format"""
    data = {}
    
    # Salary
    if request.salary:
        salary_dict = request.salary.model_dump()
        salary_dict["city"] = request.city
        if request.housing:
            salary_dict["rent_paid"] = request.housing.rent_paid_annual
        data["salary"] = salary_dict
    
    # Freelance
    if request.freelance:
        data["freelance"] = request.freelance.model_dump()
    
    # Investments
    if request.investments:
        data["investments"] = request.investments.model_dump()
    
    # Housing (for Windfall Warden)
    if request.housing:
        data["housing"] = request.housing.model_dump()
        if request.housing.rental_income > 0:
            data["rental"] = {
                "gross_rent": request.housing.rental_income,
                "municipal_taxes": request.housing.municipal_taxes,
                "home_loan_interest": request.housing.home_loan_interest,
            }
    
    # Deductions
    data["deductions"] = {
        "section_80c": request.section_80c,
        "section_80d": request.section_80d,
        "section_80ccd_1b": request.section_80ccd_1b,
    }
    
    return data

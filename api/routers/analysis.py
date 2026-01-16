from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..guardians.base import UserContext, Insight
from ..guardians.salary import SalarySentinel
from ..guardians.portfolio import PortfolioArchitect
from ..guardians.hustle import HustleShield
from ..guardians.windfall import WindfallWarden

router = APIRouter(prefix="/analysis", tags=["analysis"])

class AnalysisRequest(BaseModel):
    user_id: str
    income_details: Dict[str, float]
    regime: str = "new"
    documents_summary: Optional[List[Dict[str, Any]]] = []

class AnalysisResponse(BaseModel):
    insights: List[Insight]
    total_potential_savings: float

@router.post("/", response_model=AnalysisResponse)
async def run_analysis(request: AnalysisRequest):
    """
    Run all Guardians on the provided user context.
    """
    
    # Mapper
    context = UserContext(
        user_id=request.user_id,
        regime=request.regime,
        income_salary=request.income_details.get("salary", 0),
        income_interest=request.income_details.get("interest", 0),
        income_business=request.income_details.get("business", 0),
        capital_gains_stcg=request.income_details.get("stcg", 0),
        capital_gains_ltcg=request.income_details.get("ltcg", 0),
        investments_80c=request.income_details.get("80c", 0),
        investments_80d=request.income_details.get("80d", 0),
        investments_80ccd=request.income_details.get("80ccd", 0),
        hra_received=request.income_details.get("hra", 0),
        rent_paid=request.income_details.get("rent_paid", 0),
        documents=request.documents_summary or []
    )
    
    guardians = [
        SalarySentinel(),
        PortfolioArchitect(),
        HustleShield(),
        WindfallWarden()
    ]
    
    all_insights = []
    
    for guardian in guardians:
        try:
            insights = guardian.analyze(context)
            all_insights.extend(insights)
        except Exception as e:
            # Log error but continue with other guardians
            print(f"Error in {guardian.NAME}: {e}")
            continue
            
    # Calculate totals
    total_savings = sum(i.impact_currency for i in all_insights if i.impact_currency > 0)
    
    return AnalysisResponse(
        insights=all_insights,
        total_potential_savings=total_savings
    )

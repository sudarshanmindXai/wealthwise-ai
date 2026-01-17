from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional, Dict
from ..output.form12bb import Form12BBGenerator

router = APIRouter(prefix="/output", tags=["output"])

class UserDetails(BaseModel):
    name: str
    address: Optional[str] = ""
    pan: Optional[str] = ""
    father_name: Optional[str] = ""
    designation: Optional[str] = ""
    financial_year: Optional[str] = "2025-26"

class HraDetails(BaseModel):
    rent_paid: float = 0
    landlord_name: Optional[str] = ""
    landlord_pan: Optional[str] = ""
    address: Optional[str] = ""

class HomeLoanDetails(BaseModel):
    amount: float = 0
    lender_name: Optional[str] = ""
    lender_pan: Optional[str] = ""

class DeductionItem(BaseModel):
    description: str
    amount: float

class Form12BBRequest(BaseModel):
    user: UserDetails
    hra: HraDetails
    lta: float = 0
    home_loan_interest: HomeLoanDetails
    deductions_80c: List[DeductionItem] = []
    deductions_points: Dict[str, float] = {}

@router.post("/form12bb")
async def generate_form12bb(request: Form12BBRequest):
    """
    Generate Form 12BB PDF based on provided data.
    """
    try:
        # Convert Pydantic model to dict
        data = request.dict()
        
        generator = Form12BBGenerator(data)
        pdf_bytes = generator.generate()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Form_12BB.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ReportRequest(BaseModel):
    user: Dict
    analysis: Dict
    insights: List[Dict] = []

@router.post("/report/pdf")
async def generate_report_pdf(request: ReportRequest):
    """
    Generate Detailed Report PDF.
    """
    try:
        from ..output.report_pdf import ReportPDFGenerator
        
        data = request.dict()
        generator = ReportPDFGenerator(data)
        pdf_bytes = generator.generate()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=WealthWise_Report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

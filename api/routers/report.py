"""
WealthWise AI - Report Data Router
===================================
Aggregates extracted data for report generation.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from api.ingestion.store import get_all_tasks
from api.analysis.risk_engine import analyze_risks, RiskAlert

router = APIRouter(prefix="/report", tags=["report"])


class ReportData(BaseModel):
    """Aggregated data for Form 12BB and report generation"""
    # User Info (from salary slips/Form 16)
    user_name: Optional[str] = None
    user_pan: Optional[str] = None
    employer_name: Optional[str] = None
    designation: Optional[str] = None
    financial_year: str = "2025-26"
    
    # Salary Details
    gross_salary: float = 0
    basic_salary: float = 0
    hra_received: float = 0
    tds_deducted: float = 0
    
    # HRA Details
    rent_paid: float = 0
    landlord_name: Optional[str] = None
    landlord_pan: Optional[str] = None
    rental_address: Optional[str] = None
    
    # Deductions
    lta: float = 0
    home_loan_interest: float = 0
    home_loan_lender: Optional[str] = None
    
    # 80C Deductions
    deductions_80c: List[dict] = []
    total_80c: float = 0
    
    # Other Deductions
    deduction_80d: float = 0  # Medical Insurance
    deduction_80g: float = 0  # Donations
    
    # Investment Data from Portfolio
    ltcg: float = 0
    stcg: float = 0
    
    # Business Income (from bank statement classification)
    business_income: float = 0
    personal_income: float = 0
    
    # Risk Analysis
    risk_alerts: List[RiskAlert] = []


@router.get("/data", response_model=ReportData)
async def get_report_data():
    """
    Aggregate all extracted data for report generation.
    Collects data from all completed ingestion tasks.
    """
    all_tasks = get_all_tasks()
    report = ReportData()
    
    for task in all_tasks:
        if task.get("status") != "complete":
            continue
            
        doc_type = task.get("document_type")
        result = task.get("result", {})
        
        # Get fields as dict for easier access
        fields = {}
        for field in result.get("fields", []):
            fields[field.get("name")] = field.get("value")
        
        # Extract based on document type
        if doc_type == "form_16":
            report.gross_salary += fields.get("gross_salary", 0) or 0
            report.basic_salary += fields.get("basic", 0) or 0
            report.hra_received += fields.get("hra", 0) or 0
            report.tds_deducted += fields.get("tds_deducted", 0) or fields.get("tds", 0) or 0
            
            if fields.get("employer_name"):
                report.employer_name = fields.get("employer_name")
            if fields.get("employee_name"):
                report.user_name = fields.get("employee_name")
            if fields.get("pan"):
                report.user_pan = fields.get("pan")
                
        elif doc_type == "salary_slip":
            # Use latest salary slip values (don't accumulate monthly)
            if fields.get("gross_salary"):
                report.gross_salary = max(report.gross_salary, fields.get("gross_salary", 0) * 12)
            if fields.get("basic"):
                report.basic_salary = max(report.basic_salary, fields.get("basic", 0) * 12)
                
        elif doc_type == "bank_statement":
            report.business_income += fields.get("business_income", 0) or 0
            report.personal_income += fields.get("personal_income", 0) or 0
            
        elif doc_type == "elss_receipt":
            elss_amount = fields.get("contribution_amount", 0) or 0
            if elss_amount > 0:
                report.deductions_80c.append({
                    "description": "ELSS Investment",
                    "amount": elss_amount
                })
                report.total_80c += elss_amount
                
        elif doc_type == "zerodha_pnl" or doc_type == "broker_pl":
            report.ltcg += fields.get("ltcg", 0) or fields.get("long_term_capital_gains", 0) or 0
            report.stcg += fields.get("stcg", 0) or fields.get("short_term_capital_gains", 0) or 0
    
    # Apply limits
    report.total_80c = min(report.total_80c, 150000)  # 80C limit
    
    # Run Risk Analysis
    report.risk_alerts = analyze_risks(report.dict())
    
    return report


@router.get("/debug/tasks")
async def debug_tasks():
    """Debug endpoint to see all stored tasks"""
    all_tasks = get_all_tasks()
    return {
        "count": len(all_tasks),
        "tasks": [
            {
                "task_id": t.get("task_id"),
                "filename": t.get("filename"),
                "status": t.get("status"),
                "document_type": t.get("document_type"),
                "has_result": t.get("result") is not None,
                "result_keys": list(t.get("result", {}).keys()) if t.get("result") else [],
            }
            for t in all_tasks
        ]
    }

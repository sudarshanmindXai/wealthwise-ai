"""
WealthWise AI - Pydantic Models
================================
Request/Response schemas for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TaxRegime(str, Enum):
    OLD = "old"
    NEW = "new"


# =============================================================================
# Income Models
# =============================================================================

class SalaryInput(BaseModel):
    gross_salary: float = Field(ge=0, description="Total salary income")
    basic_salary: float = Field(ge=0, description="Basic pay")
    da: float = Field(default=0, ge=0, description="Dearness Allowance")
    hra_received: float = Field(default=0, ge=0, description="HRA component")
    employer_nps: float = Field(default=0, ge=0, description="Employer NPS (80CCD2)")
    tds_deducted: float = Field(default=0, ge=0, description="TDS already deducted")


class FreelanceInput(BaseModel):
    gross_receipts: float = Field(ge=0, description="Total professional receipts")
    cash_receipts: float = Field(default=0, ge=0, description="Cash portion of receipts")
    actual_expenses: float = Field(default=0, ge=0, description="Actual expenses incurred")
    profession_type: str = Field(default="technical_consultancy")


class InvestmentInput(BaseModel):
    ltcg_realized: float = Field(default=0, description="Realized LTCG")
    ltcg_unrealized: float = Field(default=0, description="Unrealized LTCG")
    stcg_realized: float = Field(default=0, description="Realized STCG")
    dividends: float = Field(default=0, ge=0)
    crypto_gains: float = Field(default=0, ge=0)
    crypto_losses: float = Field(default=0, ge=0)


class HousingInput(BaseModel):
    rent_paid_annual: float = Field(default=0, ge=0, description="Annual rent paid")
    is_metro: bool = Field(default=False, description="Living in metro city")
    rental_income: float = Field(default=0, ge=0, description="Rental income received")
    municipal_taxes: float = Field(default=0, ge=0)
    home_loan_interest: float = Field(default=0, ge=0)


# =============================================================================
# Request Models
# =============================================================================

class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint"""
    # Personal info
    name: Optional[str] = None
    pan: Optional[str] = None
    city: str = Field(default="", description="City of residence")
    
    # Income sources
    salary: Optional[SalaryInput] = None
    freelance: Optional[FreelanceInput] = None
    investments: Optional[InvestmentInput] = None
    housing: Optional[HousingInput] = None
    
    # Deductions
    section_80c: float = Field(default=0, ge=0, le=150000)
    section_80d: float = Field(default=0, ge=0)
    section_80ccd_1b: float = Field(default=0, ge=0, le=50000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Rohan Sharma",
                "city": "Bangalore",
                "salary": {
                    "gross_salary": 1800000,
                    "basic_salary": 900000,
                    "hra_received": 300000,
                    "employer_nps": 0
                },
                "freelance": {
                    "gross_receipts": 600000,
                    "profession_type": "technical_consultancy"
                },
                "housing": {
                    "rent_paid_annual": 240000,
                    "is_metro": True
                },
                "section_80c": 150000,
                "section_80d": 25000
            }
        }


class RegimeCompareRequest(BaseModel):
    """Request for regime comparison"""
    gross_income: float = Field(gt=0)
    deductions: float = Field(default=0, ge=0)


# =============================================================================
# Response Models
# =============================================================================

class FindingResponse(BaseModel):
    guardian: str
    severity: str
    category: str
    title: str
    description: str
    potential_savings: float = 0
    action_required: bool = False
    action_steps: list[str] = []
    related_section: Optional[str] = None


class GuardianResultResponse(BaseModel):
    guardian: str
    taxable_contribution: float
    findings: list[FindingResponse]
    metadata: dict = {}


class AnalyzeResponse(BaseModel):
    """Response from /analyze endpoint"""
    total_taxable_income: float
    total_potential_savings: float
    has_critical_findings: bool
    finding_counts: dict[str, int]
    guardians: dict[str, GuardianResultResponse]


class TaxBreakdownResponse(BaseModel):
    regime: str
    gross_income: float
    standard_deduction: float
    deductions: float
    taxable_income: float
    tax_on_slabs: float
    rebate_87a: float
    tax_after_rebate: float
    surcharge: float
    cess: float
    total_tax: float


class RegimeCompareResponse(BaseModel):
    old_regime: TaxBreakdownResponse
    new_regime: TaxBreakdownResponse
    recommended: str
    savings: float

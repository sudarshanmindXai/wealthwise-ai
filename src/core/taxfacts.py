"""
TaxFacts: Canonical Schema for Tax Computation

This is the SINGLE SOURCE OF TRUTH for all tax-related calculations.

Rules:
- Contains ONLY fields that impact tax computation (TIER 1 + TIER 2)
- NO identity fields (name, PAN, DOB, email, phone, address)
- NO UI-only fields (those go in UserIdentity schema)
- All calculations derive from this schema
- Fully auditable and deterministic

TIER 1 (MUST HAVE): Fields directly impacting tax calculations
TIER 2 (OPTIONAL): Fields enabling scenario-based optimizations
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class TaxFacts(BaseModel):
    """
    Unified data model for tax computation and scenario analysis.
    
    TIER 1: Core fields required for baseline tax calculation
    TIER 2: Optional fields enabling advanced scenarios
    Metadata: Data provenance, confidence, timestamps
    """

    # =====================================================================
    # TIER 1: MUST HAVE (Core Tax Calculation Fields)
    # =====================================================================

    # --- Taxpayer Info ---
    assessment_year: str = Field(
        ..., 
        description="Assessment year (e.g., '2025-26')",
        pattern=r"^\d{4}-\d{2}$"
    )
    
    residential_status: str = Field(
        ..., 
        description="Residential status: 'resident' or 'nri'",
        pattern=r"^(resident|nri)$"
    )
    
    age_category: str = Field(
        ..., 
        description="Age category: 'below_60', 'senior_60_80', or 'above_80'",
        pattern=r"^(below_60|senior_60_80|above_80)$"
    )
    
    huf_status: bool = Field(
        default=False,
        description="Is taxpayer an HUF (Hindu Undivided Family)?"
    )

    # --- Income: Salary ---
    salary_gross: float = Field(
        default=0.0,
        ge=0,
        description="Gross salary amount"
    )
    
    salary_standard_deduction_claim: bool = Field(
        default=True,
        description="Is standard deduction on salary claimed?"
    )
    
    salary_exempt_allowances: float = Field(
        default=0.0,
        ge=0,
        description="Total exempt allowances (HRA, DA, etc.)"
    )

    # --- Income: House Property ---
    property_count: int = Field(
        default=0,
        ge=0,
        description="Number of house properties (self-occupied + let-out)"
    )
    
    property_letout_net_income: float = Field(
        default=0.0,
        ge=0,
        description="Net income from let-out property (after all deductions)"
    )

    # --- Income: Capital Gains ---
    capital_gains_stcg_111a: float = Field(
        default=0.0,
        ge=0,
        description="Short-term capital gains under Section 111A (equity shares, mutual funds)"
    )
    
    capital_gains_stcg_other: float = Field(
        default=0.0,
        ge=0,
        description="Short-term capital gains (other than 111A)"
    )
    
    capital_gains_ltcg_112a: float = Field(
        default=0.0,
        ge=0,
        description="Long-term capital gains under Section 112A (equity)"
    )
    
    capital_gains_ltcg_other: float = Field(
        default=0.0,
        ge=0,
        description="Long-term capital gains (other than 112A)"
    )

    # --- Income: Other Sources ---
    other_income_savings_interest: float = Field(
        default=0.0,
        ge=0,
        description="Interest income from savings accounts"
    )
    
    other_income_fd_interest: float = Field(
        default=0.0,
        ge=0,
        description="Interest income from fixed deposits"
    )
    
    other_income_dividends: float = Field(
        default=0.0,
        ge=0,
        description="Dividend income (both listed and unlisted)"
    )
    
    other_income_family_pension: float = Field(
        default=0.0,
        ge=0,
        description="Family pension received"
    )
    
    other_income_other: float = Field(
        default=0.0,
        ge=0,
        description="Other income from various sources"
    )

    # --- Income: Business/Profession ---
    business_has_income: bool = Field(
        default=False,
        description="Does taxpayer have business/profession income?"
    )
    
    business_presumptive_opted: bool = Field(
        default=False,
        description="Has opted for presumptive income scheme (44AD/44ADA)?"
    )
    
    business_presumptive_section: Optional[str] = Field(
        default=None,
        pattern=r"^(44AD|44ADA|None)$|^$",
        description="Presumptive section used: '44AD', '44ADA', or null"
    )
    
    business_non_presumptive_profit: float = Field(
        default=0.0,
        ge=0,
        description="Net profit from non-presumptive business"
    )

    # --- Deductions: Section 80 (Core) ---
    deduction_80c: float = Field(
        default=0.0,
        ge=0,
        le=150000,  # Cap of ₹1.5 lakh
        description="Section 80C deductions (investments, insurance, etc.); capped at ₹1.5L"
    )
    
    deduction_80ccd_1b: float = Field(
        default=0.0,
        ge=0,
        le=50000,  # Additional NPS cap
        description="Section 80CCD(1B) - Additional NPS contribution; capped at ₹50k"
    )
    
    deduction_80d_self: float = Field(
        default=0.0,
        ge=0,
        le=50000,  # Cap for non-senior
        description="Section 80D - Medical insurance premium (self); capped at ₹50k"
    )
    
    deduction_80g: float = Field(
        default=0.0,
        ge=0,
        description="Section 80G - Charitable donations"
    )
    
    deduction_80tta: float = Field(
        default=0.0,
        ge=0,
        le=10000,  # Cap of ₹10k
        description="Section 80TTA - Savings account interest; capped at ₹10k"
    )
    
    deduction_other: float = Field(
        default=0.0,
        ge=0,
        description="Other Chapter VIA deductions (80D parent/spouse, 80E, etc.)"
    )

    # --- Home Loan: CANONICAL SOURCE ---
    home_loan_interest_paid: float = Field(
        default=0.0,
        ge=0,
        description="Interest paid on home loan during FY (Section 24); use for property deduction"
    )
    
    home_loan_principal_paid: float = Field(
        default=0.0,
        ge=0,
        description="Principal repaid on home loan during FY (informational; not deductible)"
    )

    # --- Taxes Paid ---
    taxes_tds: float = Field(
        default=0.0,
        ge=0,
        description="Tax Deducted at Source (TDS) during FY"
    )
    
    taxes_advance_tax: float = Field(
        default=0.0,
        ge=0,
        description="Advance tax paid during FY"
    )
    
    taxes_self_assessment_tax: float = Field(
        default=0.0,
        ge=0,
        description="Self-assessment tax paid during FY"
    )

    # =====================================================================
    # TIER 2: OPTIONAL (Scenario Enhancement Fields)
    # =====================================================================

    # --- Deductions: Section 80 (Advanced) ---
    deduction_80d_spouse: float = Field(
        default=0.0,
        ge=0,
        le=25000,
        description="Section 80D - Medical insurance premium (spouse); capped at ₹25k"
    )
    
    deduction_80d_children: float = Field(
        default=0.0,
        ge=0,
        le=25000,
        description="Section 80D - Medical insurance premium (children under 25); capped at ₹25k"
    )
    
    deduction_80d_parents: float = Field(
        default=0.0,
        ge=0,
        le=100000,  # Enhanced cap for seniors
        description="Section 80D - Medical insurance premium (parents, especially seniors); capped at ₹1L"
    )
    
    deduction_80e_education_loan_interest: float = Field(
        default=0.0,
        ge=0,
        description="Section 80E - Education loan interest (no specific cap, only loan-based)"
    )
    
    deduction_80ee_home_loan_interest: float = Field(
        default=0.0,
        ge=0,
        le=150000,  # Cap of ₹1.5L for first-time buyer
        description="Section 80EE - Home loan interest (first-time buyer); capped at ₹1.5L"
    )
    
    deduction_80eea_home_loan_interest: float = Field(
        default=0.0,
        ge=0,
        le=200000,  # Higher cap for seniors/new property
        description="Section 80EEA - Home loan interest (senior citizen or new property); capped at ₹2L"
    )
    
    deduction_80gg_house_rent: float = Field(
        default=0.0,
        ge=0,
        description="Section 80GG - House rent deduction (mutually exclusive with home loan interest)"
    )

    # --- Home Loan: Detailed ---
    home_loan_amount: float = Field(
        default=0.0,
        ge=0,
        description="Total sanctioned home loan amount (informational)"
    )
    
    home_loan_year_of_purchase: int = Field(
        default=0,
        ge=0,
        description="Year of property purchase (for first-time buyer determination)"
    )
    
    home_loan_first_time_buyer: bool = Field(
        default=False,
        description="Is taxpayer a first-time home buyer (affects 80EE eligibility)?"
    )

    # --- Investments: Breakdown ---
    investment_ppf_amount: float = Field(
        default=0.0,
        ge=0,
        description="Public Provident Fund (PPF) contribution amount"
    )
    
    investment_elss_amount: float = Field(
        default=0.0,
        ge=0,
        description="Equity Linked Saving Scheme (ELSS) contribution amount"
    )
    
    investment_lic_premium: float = Field(
        default=0.0,
        ge=0,
        description="Life Insurance Company (LIC) premium paid"
    )
    
    investment_nps_amount: float = Field(
        default=0.0,
        ge=0,
        description="National Pension Scheme (NPS) contribution amount"
    )

    # --- Family & Dependents ---
    spouse_name: str = Field(
        default="",
        description="TIER 3 UI-only field; included here for scenario context only"
    )
    
    spouse_pan: str = Field(
        default="",
        description="TIER 3 UI-only field; included here for scenario context only"
    )
    
    children_count: int = Field(
        default=0,
        ge=0,
        description="Number of dependent children (affects 80D calculations)"
    )
    
    children_dob: List[str] = Field(
        default_factory=list,
        description="List of children's dates of birth (YYYY-MM-DD format) for age-based calculations"
    )

    # --- Losses & Carry-Forward ---
    loss_carryforward_amount: float = Field(
        default=0.0,
        ge=0,
        description="Loss carried forward from previous assessment year"
    )
    
    loss_carryforward_year: int = Field(
        default=0,
        ge=0,
        description="Assessment year from which loss is carried forward"
    )

    # --- Refund Status ---
    previous_year_refund_status: str = Field(
        default="",
        pattern=r"^(pending|received|none|)$",
        description="Previous year refund status: 'pending', 'received', or 'none'"
    )
    
    previous_year_refund_amount: float = Field(
        default=0.0,
        ge=0,
        description="Amount of previous year refund (if status is 'received')"
    )

    # =====================================================================
    # METADATA: Data Provenance, Confidence, Timestamps
    # =====================================================================

    source_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Maps field name to data source: 'form16', 'manual', 'extracted', 'chat'"
    )
    
    confidence_mapping: Dict[str, float] = Field(
        default_factory=dict,
        description="Maps field name to confidence score (1.0 = user-entered, 0.6-0.8 = extracted)"
    )
    
    last_modified: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of last modification to TaxFacts"
    )

    # =====================================================================
    # Validation Methods
    # =====================================================================

    @validator("children_dob")
    def validate_children_dob(cls, v):
        """Ensure DOB list contains valid date strings."""
        for dob in v:
            try:
                # Basic validation: check format YYYY-MM-DD
                parts = dob.split("-")
                if len(parts) != 3 or len(parts[0]) != 4:
                    raise ValueError(f"Invalid DOB format: {dob}. Use YYYY-MM-DD.")
            except Exception as e:
                raise ValueError(f"Invalid DOB: {dob}. {str(e)}")
        return v

    @validator("residential_status")
    def validate_residential_status(cls, v):
        """Ensure valid residential status."""
        if v not in ["resident", "nri"]:
            raise ValueError("residential_status must be 'resident' or 'nri'")
        return v

    @validator("age_category")
    def validate_age_category(cls, v):
        """Ensure valid age category (as per ChatGPT's correction)."""
        if v not in ["below_60", "senior_60_80", "above_80"]:
            raise ValueError("age_category must be 'below_60', 'senior_60_80', or 'above_80'")
        return v

    @validator("assessment_year")
    def validate_assessment_year(cls, v):
        """Ensure valid assessment year format (YYYY-YY)."""
        try:
            parts = v.split("-")
            if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
                raise ValueError("Must be in format YYYY-YY (e.g., 2025-26)")
        except Exception as e:
            raise ValueError(f"Invalid assessment year: {v}. {str(e)}")
        return v

    @validator("deduction_80c")
    def cap_80c(cls, v):
        """Ensure 80C does not exceed ₹1.5L cap."""
        if v > 150000:
            raise ValueError("Section 80C capped at ₹1.5L (150,000)")
        return v

    @validator("deduction_80ccd_1b")
    def cap_80ccd_1b(cls, v):
        """Ensure 80CCD(1B) does not exceed ₹50k cap."""
        if v > 50000:
            raise ValueError("Section 80CCD(1B) capped at ₹50k (50,000)")
        return v

    @validator("deduction_80d_self")
    def cap_80d_self(cls, v):
        """Ensure 80D self does not exceed ₹50k cap (for non-seniors)."""
        if v > 50000:
            raise ValueError("Section 80D (self) capped at ₹50k (50,000) for non-seniors")
        return v

    @validator("deduction_80tta")
    def cap_80tta(cls, v):
        """Ensure 80TTA does not exceed ₹10k cap."""
        if v > 10000:
            raise ValueError("Section 80TTA capped at ₹10k (10,000)")
        return v

    class Config:
        """Pydantic config for TaxFacts."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True


# =========================================================================
# UserIdentity: SEPARATE schema for UI-only fields (TIER 3)
# =========================================================================

class UserIdentity(BaseModel):
    """
    Separate schema for identity and UI-only fields.
    
    These fields are NOT used in tax calculations.
    They improve UX without cluttering the tax computation core (TaxFacts).
    """

    # --- Personal Identity ---
    taxpayer_name: str = Field(
        default="",
        description="Full name of taxpayer"
    )
    
    taxpayer_pan: str = Field(
        default="",
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$|^$",
        description="PAN (Permanent Account Number)"
    )
    
    taxpayer_dob: str = Field(
        default="",
        description="Date of birth (YYYY-MM-DD)"
    )
    
    taxpayer_email: str = Field(
        default="",
        description="Email address"
    )
    
    taxpayer_phone: str = Field(
        default="",
        description="Phone number"
    )
    
    taxpayer_address: str = Field(
        default="",
        description="Residential address"
    )
    
    taxpayer_gender: str = Field(
        default="",
        pattern=r"^(M|F|O|)$",
        description="Gender: 'M', 'F', 'O' (Other), or empty"
    )
    
    taxpayer_marital_status: str = Field(
        default="",
        pattern=r"^(single|married|divorced|widowed|)$",
        description="Marital status"
    )

    # --- Investment Details (Account Numbers, Scheme Names) ---
    investment_ppf_account_number: str = Field(
        default="",
        description="PPF account number"
    )
    
    investment_elss_scheme_names: List[str] = Field(
        default_factory=list,
        description="List of ELSS mutual fund scheme names"
    )
    
    investment_lic_policy_number: str = Field(
        default="",
        description="LIC policy number"
    )
    
    investment_nps_account_number: str = Field(
        default="",
        description="NPS account/PRAN number"
    )

    # --- Property Details ---
    property_address: str = Field(
        default="",
        description="Address of rental/owned property"
    )
    
    property_type: str = Field(
        default="",
        pattern=r"^(residential|commercial|)$",
        description="Type of property: 'residential' or 'commercial'"
    )

    class Config:
        """Pydantic config for UserIdentity."""
        use_enum_values = True


# =========================================================================
# Combined Profile: For API responses combining both schemas
# =========================================================================

class TaxFactsWithIdentity(BaseModel):
    """
    Combined view of TaxFacts + UserIdentity for API responses.
    
    Used when returning complete profile data to frontend.
    Separates concerns while providing unified view.
    """
    
    tax_facts: TaxFacts = Field(..., description="Tax computation core")
    user_identity: UserIdentity = Field(
        default_factory=UserIdentity, 
        description="Identity and UI-only fields"
    )

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from src.core.taxfacts import UserIdentity


class DocumentPayloads(BaseModel):
    """
    Container for raw extracted data from documents.
    
    These are unprocessed dictionaries that will be passed to
    the normalization agent. No validation at this layer.
    """
    
    form16_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw data extracted from Form 16 (no validation at this layer)"
    )
    
    extracted_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw data extracted from bank statements, investment statements, etc."
    )
    
    class Config:
        extra = "allow"  # Allow other document types


class TaxProfileV2(BaseModel):
    """
    V2 request format: Supports normalized TaxFacts input + UserIdentity.
    
    This is the RECOMMENDED format for v2+ clients.
    All fields are optional to allow progressive data entry (Stage 1, 2, 3, 4).
    """
    
    profile_version: str = Field(
        default="v2",
        description="Profile version ('v2')"
    )
    
    assessment_year: str = Field(
        ...,
        description="Assessment year (e.g., '2025-26')"
    )
    
    # --- TIER 1 & TIER 2: Tax calculation fields (optional, all optional) ---
    tax_facts_input: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Partial TaxFacts from UI input (all fields optional)"
    )
    
    # --- TIER 3: Identity fields (optional) ---
    user_identity: Optional[UserIdentity] = Field(
        default=None,
        description="UserIdentity with name, PAN, DOB, email, phone, etc. (TIER 3 UI-only)"
    )
    
    # --- Document extraction (optional) ---
    document_payloads: Optional[DocumentPayloads] = Field(
        default=None,
        description="Raw extracted data from Form 16, bank statements, etc."
    )
    
    # --- Chat context (optional) ---
    chat_clarifications: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Clarifications or corrections from chat"
    )
    
    class Config:
        extra = "forbid"


class TaxProfile(BaseModel):
    """
    V1 request format: BACKWARD COMPATIBLE.
    
    Existing v1 clients continue to work unchanged.
    All v1 fields preserved as-is.
    
    New v2 clients should use TaxProfileV2 instead.
    """
    
    profile_version: str = Field(
        default="v1",
        description="Profile version ('v1')"
    )
    
    assessment_year: str = Field(
        ...,
        description="Assessment year"
    )
    
    taxpayer: Dict[str, Any] = Field(
        ...,
        description="Taxpayer info (residential_status, age_category, huf_status)"
    )
    
    income: Dict[str, Any] = Field(
        ...,
        description="Income details (salary, house_property, capital_gains, etc.)"
    )
    
    deductions_old_regime: Optional[Dict[str, float]] = Field(
        default={},
        description="Deductions applicable in old regime (80C, 80D, etc.)"
    )
    
    taxes_paid: Optional[Dict[str, float]] = Field(
        default={},
        description="Taxes paid (TDS, advance_tax, self_assessment_tax)"
    )
    
    flags: Dict[str, Any] = Field(
        ...,
        description="Flags (foreign_assets, director, unlisted_equity, etc.)"
    )

    class Config:
        extra = "forbid"


# =========================================================================
# Helper function: Convert v1 TaxProfile to v2-compatible input
# =========================================================================

def convert_v1_to_v2_input(v1_profile: TaxProfile) -> Dict[str, Any]:
    """
    Convert v1 TaxProfile request to v2 tax_facts_input format.
    
    This allows v1 clients to work with v2 normalization logic.
    
    Usage:
        v1_request = TaxProfile(...)  # Old format
        v2_input = convert_v1_to_v2_input(v1_request)
        result = normalize_tax_facts(user_input=v2_input)
    
    Args:
        v1_profile (TaxProfile): V1 format request
    
    Returns:
        Dict[str, Any]: Data ready for tax_facts_input in normalization
    """
    
    v2_input = {}
    
    # --- From taxpayer section ---
    taxpayer = v1_profile.taxpayer or {}
    v2_input['assessment_year'] = v1_profile.assessment_year
    v2_input['residential_status'] = taxpayer.get('residential_status', 'resident')
    v2_input['age_category'] = taxpayer.get('age_category', 'below_60')
    v2_input['huf_status'] = taxpayer.get('is_huf', False)
    
    # --- From income section ---
    income = v1_profile.income or {}
    
    # Salary
    salary = income.get('salary', {}) or {}
    v2_input['salary_gross'] = salary.get('gross_salary', 0)
    v2_input['salary_standard_deduction_claim'] = salary.get('standard_deduction_claim', True)
    v2_input['salary_exempt_allowances'] = salary.get('exempt_allowances', 0)
    
    # House property
    hp = income.get('house_property', {}) or {}
    v2_input['property_count'] = hp.get('count_properties', 0)
    v2_input['home_loan_interest_paid'] = hp.get('self_occupied_interest', 0)
    v2_input['property_letout_net_income'] = hp.get('let_out_net_income', 0)
    
    # Capital gains
    cg = income.get('capital_gains', {}) or {}
    v2_input['capital_gains_stcg_111a'] = cg.get('stcg_111a', 0)
    v2_input['capital_gains_stcg_other'] = cg.get('stcg_other', 0)
    v2_input['capital_gains_ltcg_112a'] = cg.get('ltcg_112a', 0)
    v2_input['capital_gains_ltcg_other'] = cg.get('ltcg_other', 0)
    
    # Other sources
    other = income.get('other_sources', {}) or {}
    v2_input['other_income_savings_interest'] = other.get('savings_interest', 0)
    v2_input['other_income_fd_interest'] = other.get('fd_interest', 0)
    v2_input['other_income_dividends'] = other.get('dividends', 0)
    v2_input['other_income_family_pension'] = other.get('family_pension', 0)
    v2_input['other_income_other'] = other.get('other_taxable_income', 0)
    
    # Business/profession
    bp = income.get('business_profession', {}) or {}
    v2_input['business_has_income'] = bp.get('has_business_income', False)
    presumptive = bp.get('presumptive', {}) or {}
    v2_input['business_presumptive_opted'] = presumptive.get('opted', False)
    v2_input['business_presumptive_section'] = presumptive.get('section', None)
    non_presumptive = bp.get('non_presumptive', {}) or {}
    v2_input['business_non_presumptive_profit'] = non_presumptive.get('net_profit', 0)
    
    # --- From deductions section ---
    deductions = v1_profile.deductions_old_regime or {}
    v2_input['deduction_80c'] = deductions.get('80c', 0)
    v2_input['deduction_80ccd_1b'] = deductions.get('80ccd_1b', 0)
    v2_input['deduction_80d_self'] = deductions.get('80d', 0)
    v2_input['deduction_80g'] = deductions.get('80g', 0)
    v2_input['deduction_80tta'] = deductions.get('80tta', 0)
    v2_input['deduction_other'] = deductions.get('other_chapter_via', 0)
    
    # --- From taxes paid section ---
    taxes = v1_profile.taxes_paid or {}
    v2_input['taxes_tds'] = taxes.get('tds', 0)
    v2_input['taxes_advance_tax'] = taxes.get('advance_tax', 0)
    v2_input['taxes_self_assessment_tax'] = taxes.get('self_assessment_tax', 0)
    
    # Remove None values (let defaults handle)
    v2_input = {k: v for k, v in v2_input.items() if v is not None}
    
    return v2_input
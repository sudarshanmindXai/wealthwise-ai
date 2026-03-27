"""
WealthWise AI - Tax Calculator Engine
======================================
Comprehensive tax calculation for Indian income tax (FY 2024-25).

Integrates:
- Income tax slabs (Old & New regime)
- Surcharge for high earners
- HRA exemption
- Section 80C/80D deductions
- Capital gains tax
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .hra import calculate_hra_exemption, HRAResult
from .deductions import calculate_deductions, DeductionInput, DeductionResult
from .capital_gains import calculate_simple_equity_gains, CapitalGainsResult


# Surcharge slabs (on tax, not income)
SURCHARGE_SLABS = [
    (50_00_000, 1_00_00_000, 0.10),   # 50L - 1Cr: 10%
    (1_00_00_000, 2_00_00_000, 0.15), # 1Cr - 2Cr: 15%
    (2_00_00_000, 5_00_00_000, 0.25), # 2Cr - 5Cr: 25%
    (5_00_00_000, float('inf'), 0.37), # >5Cr: 37%
]

# New regime has capped surcharge at 25% for income > 2Cr
NEW_REGIME_MAX_SURCHARGE_RATE = 0.25


@dataclass
class TaxResult:
    """Detailed tax calculation result"""
    regime: str
    gross_income: float
    standard_deduction: float
    hra_exemption: float
    chapter_via_deductions: float
    taxable_income: float
    tax_on_slabs: float
    rebate_87a: float
    tax_after_rebate: float
    surcharge: float
    cess: float
    total_tax: float
    
    # Optional detailed breakdowns
    hra_details: Optional[HRAResult] = None
    deduction_details: Optional[DeductionResult] = None


@dataclass
class ComparisonResult:
    """Regime comparison result"""
    old_regime: TaxResult
    new_regime: TaxResult
    recommended: str
    savings: float


@dataclass
class ComprehensiveTaxSummary:
    """Full tax computation including capital gains"""
    income_tax: TaxResult
    capital_gains: Optional[CapitalGainsResult] = None
    
    total_tax_liability: float = 0
    effective_tax_rate: float = 0
    
    def __post_init__(self):
        cg_tax = self.capital_gains.total_capital_gains_tax if self.capital_gains else 0
        self.total_tax_liability = self.income_tax.total_tax + cg_tax
        
        total_income = self.income_tax.gross_income
        if self.capital_gains:
            total_income += self.capital_gains.total_capital_gains
        
        self.effective_tax_rate = (
            (self.total_tax_liability / total_income * 100) 
            if total_income > 0 else 0
        )


def calculate_surcharge(tax_amount: float, taxable_income: float, regime: str = "new") -> float:
    """
    Calculate surcharge based on income level.
    
    Args:
        tax_amount: Tax before surcharge
        taxable_income: Total taxable income
        regime: 'old' or 'new'
    
    Returns:
        Surcharge amount
    """
    if taxable_income <= 50_00_000:
        return 0
    
    surcharge_rate = 0
    for lower, upper, rate in SURCHARGE_SLABS:
        if lower < taxable_income <= upper:
            surcharge_rate = rate
            break
        elif taxable_income > upper:
            surcharge_rate = rate  # Keep updating until we find the right slab
    
    # New regime caps surcharge at 25%
    if regime == "new" and surcharge_rate > NEW_REGIME_MAX_SURCHARGE_RATE:
        surcharge_rate = NEW_REGIME_MAX_SURCHARGE_RATE
    
    return tax_amount * surcharge_rate


def calculate_tax(
    gross_income: float,
    regime: str = "new",
    deductions: float = 0,
    hra_exemption: float = 0,
) -> TaxResult:
    """
    Calculate tax based on regime rules (FY 2024-25 / AY 2025-26).
    
    Args:
        gross_income: Total gross income
        regime: 'old' or 'new'
        deductions: Total Chapter VI-A deductions (80C, 80D, etc.)
        hra_exemption: HRA exemption amount (Section 10(13A))
    
    Returns:
        TaxResult with full breakdown
    """
    std_deduction = 50000 if regime == "old" else 75000
    
    if regime == "new":
        # New regime: No HRA or 80C deductions, only standard deduction
        taxable_income = max(0, gross_income - std_deduction)
        chapter_via = 0
        hra = 0
        
        # New Regime Slabs (FY 2024-25)
        tax = 0
        if taxable_income > 300000:
            tax += (min(taxable_income, 700000) - 300000) * 0.05
        if taxable_income > 700000:
            tax += (min(taxable_income, 1000000) - 700000) * 0.10
        if taxable_income > 1000000:
            tax += (min(taxable_income, 1200000) - 1000000) * 0.15
        if taxable_income > 1200000:
            tax += (min(taxable_income, 1500000) - 1200000) * 0.20
        if taxable_income > 1500000:
            tax += (taxable_income - 1500000) * 0.30
        
        # Rebate 87A: Taxable income up to 7L is tax free
        rebate = tax if taxable_income <= 700000 else 0
        
    else:
        # Old Regime: HRA + 80C deductions allowed
        chapter_via = deductions
        hra = hra_exemption
        taxable_income = max(0, gross_income - std_deduction - hra - chapter_via)
        
        # Old Regime Slabs
        tax = 0
        if taxable_income > 250000:
            tax += (min(taxable_income, 500000) - 250000) * 0.05
        if taxable_income > 500000:
            tax += (min(taxable_income, 1000000) - 500000) * 0.20
        if taxable_income > 1000000:
            tax += (taxable_income - 1000000) * 0.30
        
        # Rebate 87A: Taxable income up to 5L is tax free
        rebate = tax if taxable_income <= 500000 else 0

    tax_after_rebate = max(0, tax - rebate)
    
    # Surcharge
    surcharge = calculate_surcharge(tax_after_rebate, taxable_income, regime)
    
    # Cess (4% on tax + surcharge)
    cess = (tax_after_rebate + surcharge) * 0.04
    
    total_tax = tax_after_rebate + surcharge + cess

    return TaxResult(
        regime=regime,
        gross_income=gross_income,
        standard_deduction=std_deduction,
        hra_exemption=hra if regime == "old" else 0,
        chapter_via_deductions=chapter_via if regime == "old" else 0,
        taxable_income=taxable_income,
        tax_on_slabs=tax,
        rebate_87a=rebate,
        tax_after_rebate=tax_after_rebate,
        surcharge=surcharge,
        cess=cess,
        total_tax=total_tax
    )


def compare_regimes(
    gross_income: float,
    deductions: float = 0,
    hra_exemption: float = 0
) -> ComparisonResult:
    """
    Compare old vs new regime and recommend the better option.
    
    Args:
        gross_income: Total gross income
        deductions: Chapter VI-A deductions (used only in old regime)
        hra_exemption: HRA exemption (used only in old regime)
    
    Returns:
        ComparisonResult with recommendation
    """
    old = calculate_tax(gross_income, "old", deductions, hra_exemption)
    new = calculate_tax(gross_income, "new", 0, 0)
    
    if new.total_tax < old.total_tax:
        rec = "new"
        savings = old.total_tax - new.total_tax
    else:
        rec = "old"
        savings = new.total_tax - old.total_tax
    
    return ComparisonResult(
        old_regime=old,
        new_regime=new,
        recommended=rec,
        savings=savings
    )


def calculate_comprehensive_tax(
    gross_income: float,
    regime: str = "new",
    deduction_input: Optional[DeductionInput] = None,
    hra_params: Optional[Dict] = None,
    ltcg: float = 0,
    stcg: float = 0,
    crypto_gains: float = 0
) -> ComprehensiveTaxSummary:
    """
    Full tax calculation including capital gains.
    
    Args:
        gross_income: Salary/business income
        regime: 'old' or 'new'
        deduction_input: DeductionInput for 80C/80D calculations
        hra_params: Dict with hra_received, basic_salary, rent_paid, city
        ltcg: Equity LTCG
        stcg: Equity STCG
        crypto_gains: Crypto gains
    
    Returns:
        ComprehensiveTaxSummary with full breakdown
    """
    # Calculate HRA exemption
    hra_result = None
    hra_exemption = 0
    if hra_params and regime == "old":
        hra_result = calculate_hra_exemption(**hra_params)
        hra_exemption = hra_result.exemption
    
    # Calculate deductions
    deduction_result = None
    deductions = 0
    if deduction_input and regime == "old":
        deduction_result = calculate_deductions(deduction_input)
        deductions = deduction_result.total_deductions
    
    # Income tax
    income_tax = calculate_tax(gross_income, regime, deductions, hra_exemption)
    income_tax.hra_details = hra_result
    income_tax.deduction_details = deduction_result
    
    # Capital gains
    cg_result = None
    if ltcg > 0 or stcg > 0 or crypto_gains > 0:
        cg_result = calculate_simple_equity_gains(ltcg, stcg, crypto_gains)
    
    return ComprehensiveTaxSummary(
        income_tax=income_tax,
        capital_gains=cg_result
    )

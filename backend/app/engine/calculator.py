"""
WealthWise AI - Deterministic Tax Calculator
============================================
THE TRUTH LAYER - All tax calculations.
NO LLM MATH. Pure Python deterministic logic.

FY: 2025-26 (AY: 2026-27)
Budget: Union Budget 2025 Enacted
"""

from typing import Literal, Optional
from dataclasses import dataclass
from .constants import (
    NEW_REGIME_SLABS,
    OLD_REGIME_SLABS,
    STANDARD_DEDUCTION_NEW,
    STANDARD_DEDUCTION_OLD,
    REBATE_87A,
    MARGINAL_RELIEF_CEILING,
    SURCHARGE_NEW,
    SURCHARGE_OLD,
    CESS_RATE,
    LTCG_RATE,
    LTCG_EXEMPTION,
    STCG_EQUITY_RATE,
    CRYPTO_TAX_RATE,
)


@dataclass
class TaxBreakdown:
    """Detailed tax calculation breakdown"""
    regime: str
    gross_income: float
    standard_deduction: float
    deductions: float
    taxable_income: float
    tax_on_slabs: float
    rebate_87a: float
    marginal_relief_applied: bool
    tax_after_rebate: float
    surcharge: float
    cess: float
    total_tax: float


# =============================================================================
# SLAB CALCULATIONS
# =============================================================================

def calculate_slab_tax(income: float, slabs: list[tuple[float, float]]) -> float:
    """
    Calculate tax based on progressive slabs.
    
    Args:
        income: Taxable income
        slabs: List of (threshold, rate) tuples
    
    Returns:
        Tax amount before rebate/surcharge/cess
    """
    if income <= 0:
        return 0.0
    
    tax = 0.0
    prev_threshold = 0.0
    
    for threshold, rate in slabs:
        if income <= prev_threshold:
            break
        
        taxable_in_slab = min(income, threshold) - prev_threshold
        if taxable_in_slab > 0:
            tax += taxable_in_slab * rate
        
        prev_threshold = threshold
    
    return tax


def calculate_new_regime_slab_tax(income: float) -> float:
    """Calculate tax using New Regime slabs (Budget 2025)"""
    return calculate_slab_tax(income, NEW_REGIME_SLABS)


def calculate_old_regime_slab_tax(income: float) -> float:
    """Calculate tax using Old Regime slabs"""
    return calculate_slab_tax(income, OLD_REGIME_SLABS)


# =============================================================================
# REBATE & MARGINAL RELIEF (Section 87A)
# =============================================================================

def apply_rebate_87a(
    tax: float,
    taxable_income: float,
    regime: Literal["new", "old"]
) -> tuple[float, float, bool]:
    """
    Apply Section 87A rebate with marginal relief.
    
    Returns:
        (tax_after_rebate, rebate_amount, marginal_relief_applied)
    """
    rebate_config = REBATE_87A[regime]
    threshold = rebate_config["threshold"]
    max_rebate = rebate_config["max_rebate"]
    
    # Full rebate if under threshold
    if taxable_income <= threshold:
        rebate = min(tax, max_rebate)
        return (0.0, rebate, False)
    
    # Marginal Relief for New Regime (cliff protection)
    if regime == "new" and taxable_income > threshold and taxable_income <= MARGINAL_RELIEF_CEILING:
        excess_income = taxable_income - threshold
        # Tax cannot exceed money earned over threshold
        if tax > excess_income:
            return (excess_income, 0.0, True)
    
    # No rebate above threshold
    return (tax, 0.0, False)


# =============================================================================
# SURCHARGE
# =============================================================================

def calculate_surcharge(
    tax: float,
    total_income: float,
    regime: Literal["new", "old"]
) -> float:
    """
    Calculate surcharge based on income and regime.
    New Regime: Capped at 25%
    Old Regime: Up to 37%
    """
    slabs = SURCHARGE_NEW if regime == "new" else SURCHARGE_OLD
    
    prev_threshold = 0
    rate = 0.0
    
    for threshold, slab_rate in slabs:
        if total_income <= threshold:
            break
        rate = slab_rate
        prev_threshold = threshold
    
    return tax * rate


# =============================================================================
# CESS
# =============================================================================

def calculate_cess(tax_plus_surcharge: float) -> float:
    """Calculate 4% Health & Education Cess"""
    return tax_plus_surcharge * CESS_RATE


# =============================================================================
# CAPITAL GAINS TAX
# =============================================================================

def calculate_ltcg_tax(ltcg: float) -> float:
    """
    Calculate LTCG tax on equity (Section 112A)
    12.5% on gains above ₹1.25L exemption
    """
    taxable = max(0, ltcg - LTCG_EXEMPTION)
    return taxable * LTCG_RATE


def calculate_stcg_tax(stcg: float) -> float:
    """
    Calculate STCG tax on equity (Section 111A)
    Flat 20%
    """
    return max(0, stcg) * STCG_EQUITY_RATE


def calculate_crypto_tax(gains: float) -> float:
    """
    Calculate Crypto/VDA tax (Section 115BBH)
    Flat 30% - No set-off allowed
    """
    return max(0, gains) * CRYPTO_TAX_RATE


# =============================================================================
# MAIN CALCULATOR
# =============================================================================

def calculate_tax(
    gross_income: float,
    regime: Literal["new", "old"] = "new",
    deductions: float = 0.0,
    apply_standard_deduction: bool = True,
) -> TaxBreakdown:
    """
    Calculate total tax liability.
    
    Args:
        gross_income: Total income before deductions
        regime: "new" or "old"
        deductions: Chapter VI-A deductions (only for old regime)
        apply_standard_deduction: Whether to apply standard deduction
    
    Returns:
        TaxBreakdown with detailed calculation
    """
    # Standard Deduction
    std_ded = 0.0
    if apply_standard_deduction:
        std_ded = STANDARD_DEDUCTION_NEW if regime == "new" else STANDARD_DEDUCTION_OLD
    
    # Only Old Regime allows full deductions
    if regime == "new":
        deductions = 0.0  # New regime doesn't allow most deductions
    
    # Taxable Income
    taxable_income = max(0, gross_income - std_ded - deductions)
    
    # Slab Tax
    if regime == "new":
        tax_on_slabs = calculate_new_regime_slab_tax(taxable_income)
    else:
        tax_on_slabs = calculate_old_regime_slab_tax(taxable_income)
    
    # Rebate 87A (with Marginal Relief)
    tax_after_rebate, rebate, marginal_applied = apply_rebate_87a(
        tax_on_slabs, taxable_income, regime
    )
    
    # Surcharge
    surcharge = calculate_surcharge(tax_after_rebate, gross_income, regime)
    
    # Cess
    cess = calculate_cess(tax_after_rebate + surcharge)
    
    # Total
    total_tax = tax_after_rebate + surcharge + cess
    
    return TaxBreakdown(
        regime=regime,
        gross_income=gross_income,
        standard_deduction=std_ded,
        deductions=deductions,
        taxable_income=taxable_income,
        tax_on_slabs=tax_on_slabs,
        rebate_87a=rebate,
        marginal_relief_applied=marginal_applied,
        tax_after_rebate=tax_after_rebate,
        surcharge=surcharge,
        cess=cess,
        total_tax=total_tax,
    )


def calculate_tax_simple(
    income: float,
    regime: Literal["new", "old"] = "new"
) -> float:
    """
    Simple interface - returns just the total tax.
    Used for testing marginal relief checkpoint.
    """
    result = calculate_tax(income, regime)
    return result.tax_after_rebate  # Before cess for checkpoint


def calculate_tax_on_taxable_income(
    taxable_income: float,
    regime: Literal["new", "old"] = "new"
) -> TaxBreakdown:
    """
    Calculate tax on NET TAXABLE INCOME (after all deductions).
    Used for direct testing per TEST_SCENARIOS.md
    
    Args:
        taxable_income: Income AFTER standard deduction & Chapter VI-A
        regime: "new" or "old"
    """
    return calculate_tax(
        gross_income=taxable_income,
        regime=regime,
        deductions=0,
        apply_standard_deduction=False,
    )


# =============================================================================
# REGIME COMPARISON
# =============================================================================

@dataclass
class RegimeComparison:
    """Compare Old vs New regime"""
    old_regime: TaxBreakdown
    new_regime: TaxBreakdown
    recommended: str
    savings: float


def compare_regimes(
    gross_income: float,
    deductions: float = 0.0,
) -> RegimeComparison:
    """
    Compare Old and New regime to recommend optimal choice.
    """
    old = calculate_tax(gross_income, regime="old", deductions=deductions)
    new = calculate_tax(gross_income, regime="new", deductions=0)
    
    if old.total_tax <= new.total_tax:
        recommended = "old"
        savings = new.total_tax - old.total_tax
    else:
        recommended = "new"
        savings = old.total_tax - new.total_tax
    
    return RegimeComparison(
        old_regime=old,
        new_regime=new,
        recommended=recommended,
        savings=savings,
    )

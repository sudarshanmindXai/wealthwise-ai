"""
WealthWise AI - Tax Calculator Engine
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TaxResult:
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

@dataclass
class ComparisonResult:
    old_regime: TaxResult
    new_regime: TaxResult
    recommended: str
    savings: float

def calculate_tax(gross_income: float, regime: str = "new", deductions: float = 0) -> TaxResult:
    """
    Calculate tax based on regime rules (FY 2024-25 / AY 2025-26).
    """
    std_deduction = 50000 if regime == "old" else 75000  # New regime increased to 75k
    
    if regime == "new":
        # New Regime Slabs (FY 2024-25)
        # 0-3L: Nil
        # 3-7L: 5%
        # 7-10L: 10%
        # 10-12L: 15%
        # 12-15L: 20%
        # >15L: 30%
        taxable_income = max(0, gross_income - std_deduction) # No 80C usually
        
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
            
        # Rebate 87A: Taxable income up to 7L is tax free under new regime
        rebate = 0
        if taxable_income <= 700000:
            rebate = tax
            
    else:
        # Old Regime Slabs
        # 0-2.5L: Nil
        # 2.5-5L: 5%
        # 5-10L: 20%
        # >10L: 30%
        taxable_income = max(0, gross_income - std_deduction - deductions)
        
        tax = 0
        if taxable_income > 250000:
            tax += (min(taxable_income, 500000) - 250000) * 0.05
        if taxable_income > 500000:
            tax += (min(taxable_income, 1000000) - 500000) * 0.20
        if taxable_income > 1000000:
            tax += (taxable_income - 1000000) * 0.30
            
        # Rebate 87A: Taxable income up to 5L is tax free
        rebate = 0
        if taxable_income <= 500000:
            rebate = tax

    tax_after_rebate = max(0, tax - rebate)
    cess = tax_after_rebate * 0.04
    total_tax = tax_after_rebate + cess

    return TaxResult(
        regime=regime,
        gross_income=gross_income,
        standard_deduction=std_deduction,
        deductions=deductions if regime == "old" else 0, # Simplify
        taxable_income=taxable_income,
        tax_on_slabs=tax,
        rebate_87a=rebate,
        tax_after_rebate=tax_after_rebate,
        surcharge=0, # Ignored for now
        cess=cess,
        total_tax=total_tax
    )

def compare_regimes(gross_income: float, deductions: float) -> ComparisonResult:
    old = calculate_tax(gross_income, "old", deductions)
    new = calculate_tax(gross_income, "new", deductions)
    
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

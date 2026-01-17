"""
WealthWise AI - Capital Gains Tax Calculator
=============================================
Calculates LTCG, STCG for equity, debt, property, and crypto.

FY 2024-25 Rules (Union Budget 2024):
- Equity LTCG: 12.5% above ₹1.25L exemption (holding > 12 months)
- Equity STCG: 20% (holding < 12 months)
- Debt LTCG: Taxed at slab rate (no indexation benefit from FY 2023-24)
- Property LTCG: 12.5% without indexation (Budget 2024 change)
- Crypto/VDA: 30% flat + 4% cess (no deductions except cost)
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AssetType(Enum):
    EQUITY = "equity"           # Listed shares, equity MFs
    DEBT = "debt"               # Debt MFs, bonds
    PROPERTY = "property"       # Real estate
    GOLD = "gold"               # Physical gold, gold ETFs
    CRYPTO = "crypto"           # VDAs - Virtual Digital Assets
    OTHER = "other"


@dataclass
class CapitalGain:
    """A single capital gain/loss entry"""
    asset_type: AssetType
    purchase_date: str  # YYYY-MM-DD
    sale_date: str
    purchase_value: float
    sale_value: float
    holding_months: int = 0  # Calculated
    is_long_term: bool = False  # Calculated
    gain: float = 0  # Calculated
    

@dataclass
class CapitalGainsResult:
    """Aggregated capital gains tax calculation"""
    # Equity
    equity_ltcg_gross: float = 0
    equity_ltcg_exemption: float = 0  # 1.25L
    equity_ltcg_taxable: float = 0
    equity_ltcg_tax: float = 0  # 12.5%
    equity_stcg: float = 0
    equity_stcg_tax: float = 0  # 20%
    
    # Debt (taxed at slab, so we just report the amount)
    debt_gains: float = 0
    debt_gains_note: str = "Added to income, taxed at slab rate"
    
    # Property
    property_ltcg: float = 0
    property_ltcg_tax: float = 0  # 12.5%
    
    # Crypto
    crypto_gains: float = 0
    crypto_tax: float = 0  # 30%
    
    # Totals
    total_capital_gains: float = 0
    total_capital_gains_tax: float = 0


# LTCG holding periods (months)
LTCG_HOLDING_PERIODS = {
    AssetType.EQUITY: 12,
    AssetType.DEBT: 36,  # But taxed at slab anyway now
    AssetType.PROPERTY: 24,
    AssetType.GOLD: 24,  # 36 before Budget 2024
    AssetType.CRYPTO: None,  # No LTCG concept, always 30%
}

# Tax rates
EQUITY_LTCG_RATE = 0.125  # 12.5%
EQUITY_STCG_RATE = 0.20   # 20%
EQUITY_LTCG_EXEMPTION = 125000  # ₹1.25L
PROPERTY_LTCG_RATE = 0.125  # 12.5% without indexation
CRYPTO_RATE = 0.30  # 30% flat


def calculate_capital_gains(gains: list[CapitalGain]) -> CapitalGainsResult:
    """
    Calculate capital gains tax for a list of transactions.
    
    Args:
        gains: List of CapitalGain entries
    
    Returns:
        CapitalGainsResult with tax breakdown
    """
    result = CapitalGainsResult()
    
    equity_ltcg_total = 0
    equity_stcg_total = 0
    debt_total = 0
    property_ltcg_total = 0
    crypto_total = 0
    
    for g in gains:
        gain = g.sale_value - g.purchase_value
        
        # Determine if long-term
        holding_period = LTCG_HOLDING_PERIODS.get(g.asset_type, 12)
        is_lt = g.holding_months >= holding_period if holding_period else False
        
        if g.asset_type == AssetType.EQUITY:
            if is_lt:
                equity_ltcg_total += gain
            else:
                equity_stcg_total += gain
                
        elif g.asset_type == AssetType.DEBT:
            debt_total += gain  # Taxed at slab now
            
        elif g.asset_type == AssetType.PROPERTY:
            if is_lt:
                property_ltcg_total += gain
            else:
                debt_total += gain  # STCG on property = slab rate
                
        elif g.asset_type == AssetType.CRYPTO:
            crypto_total += max(0, gain)  # No loss offset allowed
            
        elif g.asset_type == AssetType.GOLD:
            if is_lt:
                property_ltcg_total += gain  # Same rate as property
            else:
                debt_total += gain
    
    # === Equity LTCG ===
    result.equity_ltcg_gross = equity_ltcg_total
    result.equity_ltcg_exemption = min(max(0, equity_ltcg_total), EQUITY_LTCG_EXEMPTION)
    result.equity_ltcg_taxable = max(0, equity_ltcg_total - EQUITY_LTCG_EXEMPTION)
    result.equity_ltcg_tax = result.equity_ltcg_taxable * EQUITY_LTCG_RATE
    
    # === Equity STCG ===
    result.equity_stcg = equity_stcg_total
    result.equity_stcg_tax = max(0, equity_stcg_total) * EQUITY_STCG_RATE
    
    # === Debt (just report, added to income) ===
    result.debt_gains = debt_total
    
    # === Property LTCG ===
    result.property_ltcg = property_ltcg_total
    result.property_ltcg_tax = max(0, property_ltcg_total) * PROPERTY_LTCG_RATE
    
    # === Crypto ===
    result.crypto_gains = crypto_total
    result.crypto_tax = crypto_total * CRYPTO_RATE
    
    # === Totals ===
    result.total_capital_gains = (
        equity_ltcg_total + equity_stcg_total + debt_total + 
        property_ltcg_total + crypto_total
    )
    result.total_capital_gains_tax = (
        result.equity_ltcg_tax + result.equity_stcg_tax +
        result.property_ltcg_tax + result.crypto_tax
    )
    # Note: Debt gains tax is added to regular income, not counted here
    
    return result


def calculate_simple_equity_gains(
    ltcg: float = 0,
    stcg: float = 0,
    crypto: float = 0
) -> CapitalGainsResult:
    """
    Simplified calculation for dashboard use.
    
    Args:
        ltcg: Total equity LTCG
        stcg: Total equity STCG
        crypto: Total crypto gains
    
    Returns:
        CapitalGainsResult
    """
    result = CapitalGainsResult()
    
    # Equity LTCG
    result.equity_ltcg_gross = ltcg
    result.equity_ltcg_exemption = min(max(0, ltcg), EQUITY_LTCG_EXEMPTION)
    result.equity_ltcg_taxable = max(0, ltcg - EQUITY_LTCG_EXEMPTION)
    result.equity_ltcg_tax = result.equity_ltcg_taxable * EQUITY_LTCG_RATE
    
    # Equity STCG
    result.equity_stcg = stcg
    result.equity_stcg_tax = max(0, stcg) * EQUITY_STCG_RATE
    
    # Crypto
    result.crypto_gains = crypto
    result.crypto_tax = max(0, crypto) * CRYPTO_RATE
    
    result.total_capital_gains = ltcg + stcg + crypto
    result.total_capital_gains_tax = (
        result.equity_ltcg_tax + result.equity_stcg_tax + result.crypto_tax
    )
    
    return result

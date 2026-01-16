"""
WealthWise AI - Portfolio Architect
====================================
Agent 2: Analyzes investment income for optimization.

Responsibilities:
- LTCG harvesting (Section 112A)
- Buyback trap warning (Section 2(22)(f))
- Crypto guardrails (Section 115BBH)
- STCG calculation
"""

from dataclasses import dataclass
from typing import Optional

from .base import (
    BaseGuardian,
    GuardianType,
    GuardianResult,
    Finding,
    Severity,
    Category,
)
from ..engine.constants import (
    LTCG_RATE,
    LTCG_EXEMPTION,
    STCG_EQUITY_RATE,
    CRYPTO_TAX_RATE,
    CRYPTO_SET_OFF_ALLOWED,
)


@dataclass
class PortfolioData:
    """Input data for Portfolio Architect"""
    ltcg_realized: float = 0.0
    ltcg_unrealized: float = 0.0
    stcg_realized: float = 0.0
    dividends: float = 0.0
    crypto_gains: float = 0.0
    crypto_losses: float = 0.0
    has_buyback_offer: bool = False
    user_marginal_rate: float = 0.30  # Assume 30% slab


class PortfolioArchitect(BaseGuardian):
    """
    The Portfolio Architect Guardian
    
    Optimizations:
    1. LTCG Harvesting - Utilize ₹1.25L exemption
    2. Buyback Guard - Warn against buybacks at high slab
    3. Crypto Trap - Enforce no set-off rule
    """
    
    guardian_type = GuardianType.PORTFOLIO_ARCHITECT
    
    def analyze(self, data: dict) -> GuardianResult:
        """Analyze portfolio data for optimization opportunities"""
        portfolio = self._parse_portfolio_data(data)
        findings = []
        
        # Calculate actual taxes
        ltcg_tax, stcg_tax, crypto_tax = self._calculate_taxes(portfolio)
        
        # Check harvesting opportunity
        harvest_finding = self._check_harvesting(portfolio)
        if harvest_finding:
            findings.append(harvest_finding)
        
        # Check buyback trap
        buyback_finding = self._check_buyback_trap(portfolio)
        if buyback_finding:
            findings.append(buyback_finding)
        
        # Check crypto isolation
        crypto_finding = self._check_crypto_trap(portfolio)
        if crypto_finding:
            findings.append(crypto_finding)
        
        # Total capital gains income
        total_cg_income = (
            max(0, portfolio.ltcg_realized - LTCG_EXEMPTION) +
            portfolio.stcg_realized +
            portfolio.crypto_gains  # Crypto gains taxed separately
        )
        
        return GuardianResult(
            guardian=self.guardian_type,
            findings=findings,
            taxable_income_contribution=total_cg_income,
            metadata={
                "ltcg_tax": ltcg_tax,
                "stcg_tax": stcg_tax,
                "crypto_tax": crypto_tax,
                "ltcg_exemption_used": min(portfolio.ltcg_realized, LTCG_EXEMPTION),
            }
        )
    
    def _parse_portfolio_data(self, data: dict) -> PortfolioData:
        """Parse raw data into PortfolioData"""
        inv_data = data.get("investments", data)
        
        return PortfolioData(
            ltcg_realized=inv_data.get("ltcg_equity", inv_data.get("ltcg_realized", 0)),
            ltcg_unrealized=inv_data.get("ltcg_unrealized", 0),
            stcg_realized=inv_data.get("stcg_equity", inv_data.get("stcg_realized", 0)),
            dividends=inv_data.get("dividends", 0),
            crypto_gains=inv_data.get("crypto_gains", 0),
            crypto_losses=inv_data.get("crypto_losses", 0),
            has_buyback_offer=inv_data.get("has_buyback_offer", False),
            user_marginal_rate=data.get("marginal_rate", 0.30),
        )
    
    def _calculate_taxes(self, portfolio: PortfolioData) -> tuple[float, float, float]:
        """Calculate taxes on capital gains"""
        # LTCG: 12.5% on gains above ₹1.25L
        taxable_ltcg = max(0, portfolio.ltcg_realized - LTCG_EXEMPTION)
        ltcg_tax = taxable_ltcg * LTCG_RATE
        
        # STCG: 20%
        stcg_tax = max(0, portfolio.stcg_realized) * STCG_EQUITY_RATE
        
        # Crypto: 30% flat on gains only (no set-off)
        crypto_tax = max(0, portfolio.crypto_gains) * CRYPTO_TAX_RATE
        
        return ltcg_tax, stcg_tax, crypto_tax
    
    def _check_harvesting(self, portfolio: PortfolioData) -> Optional[Finding]:
        """
        Check if LTCG exemption is under-utilized.
        If realized LTCG < ₹1.25L and unrealized gains exist, recommend harvesting.
        """
        remaining_exemption = LTCG_EXEMPTION - portfolio.ltcg_realized
        
        if remaining_exemption > 10000 and portfolio.ltcg_unrealized > 0:
            harvestable = min(remaining_exemption, portfolio.ltcg_unrealized)
            tax_saved = harvestable * LTCG_RATE
            
            return Finding(
                guardian=self.guardian_type,
                code="HARVESTING_OPPORTUNITY",
                severity=Severity.INFO,
                category=Category.OPTIMIZATION,
                title="LTCG Harvesting Opportunity",
                description=(
                    f"You have ₹{remaining_exemption:,.0f} unused LTCG exemption this year. "
                    f"Consider selling and rebuying stocks with unrealized gains to reset cost basis."
                ),
                potential_savings=tax_saved,
                action_required=False,
                action_steps=[
                    f"Identify stocks with unrealized LTCG up to ₹{harvestable:,.0f}",
                    "Sell before March 31 to book gains",
                    "Rebuy immediately to maintain position",
                    "No tax on LTCG up to ₹1.25L under Section 112A",
                ],
                related_section="112A",
            )
        
        # If LTCG is within exemption
        if portfolio.ltcg_realized > 0 and portfolio.ltcg_realized <= LTCG_EXEMPTION:
            return Finding(
                guardian=self.guardian_type,
                code="LTCG_EXEMPTION_OPTIMIZED",
                severity=Severity.INFO,
                category=Category.INFORMATION,
                title="LTCG Within Exemption Limit",
                description=(
                    f"Your LTCG of ₹{portfolio.ltcg_realized:,.0f} is within the "
                    f"₹{LTCG_EXEMPTION:,.0f} exemption. No tax payable on equity gains."
                ),
                related_section="112A",
            )
        
        return None
    
    def _check_buyback_trap(self, portfolio: PortfolioData) -> Optional[Finding]:
        """
        Warn against share buybacks if user is in high tax bracket.
        Post FY26, buybacks are taxed as deemed dividend at slab rate.
        """
        if not portfolio.has_buyback_offer:
            return None
        
        if portfolio.user_marginal_rate > LTCG_RATE:
            return Finding(
                guardian=self.guardian_type,
                code="BUYBACK_WARNING",
                severity=Severity.CRITICAL,
                category=Category.RISK,
                title="Buyback Trap Warning!",
                description=(
                    f"Share buyback is now taxed as deemed dividend at your slab rate "
                    f"({portfolio.user_marginal_rate*100:.0f}%), not LTCG ({LTCG_RATE*100}%). "
                    f"Selling on open market saves {(portfolio.user_marginal_rate - LTCG_RATE)*100:.1f}% tax."
                ),
                potential_savings=0,  # Depends on buyback amount
                action_required=True,
                action_steps=[
                    "DO NOT participate in the buyback",
                    "Sell shares on open market instead",
                    f"Open market sale: {LTCG_RATE*100}% LTCG tax",
                    f"Buyback: {portfolio.user_marginal_rate*100:.0f}% slab rate tax",
                ],
                related_section="2(22)(f)",
            )
        
        return None
    
    def _check_crypto_trap(self, portfolio: PortfolioData) -> Optional[Finding]:
        """
        Warn that crypto losses cannot offset any income.
        Section 115BBH enforces strict isolation.
        """
        if portfolio.crypto_losses > 0:
            return Finding(
                guardian=self.guardian_type,
                code="CRYPTO_LOSS_DEAD",
                severity=Severity.WARNING,
                category=Category.COMPLIANCE,
                title="Crypto Loss Cannot Be Set Off",
                description=(
                    f"Your crypto loss of ₹{portfolio.crypto_losses:,.0f} is a 'dead loss'. "
                    f"Under Section 115BBH, VDA losses cannot offset crypto gains, salary, "
                    f"or any other income. This is a permanent loss with no tax benefit."
                ),
                action_required=False,
                action_steps=[
                    "Crypto losses cannot be carried forward",
                    "Cannot offset against crypto gains",
                    "Cannot offset against any other income",
                    "Consider this in future investment decisions",
                ],
                related_section="115BBH",
            )
        
        return None


# Export
__all__ = ["PortfolioArchitect", "PortfolioData"]

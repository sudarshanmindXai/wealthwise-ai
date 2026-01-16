"""
WealthWise AI - Windfall Warden
================================
Agent 4: Analyzes rental, gifts, and other income.

Responsibilities:
- Rental income with Section 24 deduction
- Gift taxation (relative vs non-relative)
- HUF clubbing provisions (Section 64)
"""

from dataclasses import dataclass
from typing import Optional, Literal

from .base import (
    BaseGuardian,
    GuardianType,
    GuardianResult,
    Finding,
    Severity,
    Category,
)
from ..engine.constants import (
    RENTAL_STANDARD_DEDUCTION,
    HOME_LOAN_INTEREST_SELF_OCCUPIED,
    GIFT_EXEMPTION_NON_RELATIVE,
)


# Relatives under Income Tax Act (exempt from gift tax)
RELATIVES = [
    "spouse", "brother", "sister", "parent", "grandparent",
    "child", "grandchild", "spouse_of_above", "in_laws"
]


@dataclass
class RentalData:
    """Rental income data"""
    gross_rent: float = 0.0
    municipal_taxes: float = 0.0
    home_loan_interest: float = 0.0
    is_self_occupied: bool = False


@dataclass
class GiftData:
    """Gift received data"""
    amount: float = 0.0
    from_relative: bool = False
    relation: str = ""
    occasion: str = ""  # marriage, inheritance, etc.


@dataclass
class HUFData:
    """HUF income data"""
    huf_income: float = 0.0
    fund_source: str = ""  # personal, ancestors, etc.
    is_personal_transfer: bool = False


@dataclass
class WindfallData:
    """Combined input for Windfall Warden"""
    rental: Optional[RentalData] = None
    gifts: list[GiftData] = None
    huf: Optional[HUFData] = None
    interest_income: float = 0.0


class WindfallWarden(BaseGuardian):
    """
    The Windfall Warden Guardian
    
    Optimizations:
    1. Rental Income - Auto-apply 30% standard deduction
    2. Gift Taxation - Filter relative vs non-relative
    3. HUF Clubbing - Check Section 64(2) violations
    """
    
    guardian_type = GuardianType.WINDFALL_WARDEN
    
    def analyze(self, data: dict) -> GuardianResult:
        """Analyze other income for optimization opportunities"""
        windfall = self._parse_windfall_data(data)
        findings = []
        taxable_income = 0.0
        
        # Process rental income
        if windfall.rental and windfall.rental.gross_rent > 0:
            rental_finding, rental_taxable = self._process_rental(windfall.rental)
            if rental_finding:
                findings.append(rental_finding)
            taxable_income += rental_taxable
        
        # Process gifts
        if windfall.gifts:
            gift_findings, gift_taxable = self._process_gifts(windfall.gifts)
            findings.extend(gift_findings)
            taxable_income += gift_taxable
        
        # Process HUF
        if windfall.huf and windfall.huf.huf_income > 0:
            huf_finding = self._check_huf_clubbing(windfall.huf)
            if huf_finding:
                findings.append(huf_finding)
                # If clubbing applies, add to individual's income
                if windfall.huf.is_personal_transfer:
                    taxable_income += windfall.huf.huf_income
        
        # Add interest income
        taxable_income += windfall.interest_income
        
        return GuardianResult(
            guardian=self.guardian_type,
            findings=findings,
            taxable_income_contribution=taxable_income,
            metadata={
                "rental_taxable": taxable_income - windfall.interest_income if windfall.rental else 0,
                "interest_income": windfall.interest_income,
            }
        )
    
    def _parse_windfall_data(self, data: dict) -> WindfallData:
        """Parse raw data into WindfallData"""
        # Parse rental
        rental_data = data.get("rental", data.get("housing", {}))
        rental = None
        if rental_data:
            rental = RentalData(
                gross_rent=rental_data.get("gross_rent", rental_data.get("rent_received", 0)),
                municipal_taxes=rental_data.get("municipal_taxes", 0),
                home_loan_interest=rental_data.get("home_loan_interest", 0),
                is_self_occupied=rental_data.get("is_self_occupied", False),
            )
        
        # Parse gifts
        gifts_data = data.get("gifts", [])
        gifts = []
        for g in gifts_data:
            gifts.append(GiftData(
                amount=g.get("amount", 0),
                from_relative=g.get("from_relative", False),
                relation=g.get("relation", ""),
                occasion=g.get("occasion", ""),
            ))
        
        # Parse HUF
        huf_data = data.get("huf", {})
        huf = None
        if huf_data:
            huf = HUFData(
                huf_income=huf_data.get("huf_income", huf_data.get("income", 0)),
                fund_source=huf_data.get("fund_source", ""),
                is_personal_transfer=huf_data.get("is_personal_transfer", False),
            )
        
        return WindfallData(
            rental=rental,
            gifts=gifts if gifts else None,
            huf=huf,
            interest_income=data.get("interest_income", 0),
        )
    
    def _process_rental(self, rental: RentalData) -> tuple[Optional[Finding], float]:
        """
        Process rental income with Section 24 deductions.
        NAV = Gross Rent - Municipal Taxes
        Taxable = NAV - 30% Standard Deduction - Home Loan Interest
        """
        nav = rental.gross_rent - rental.municipal_taxes
        standard_ded = nav * RENTAL_STANDARD_DEDUCTION
        
        # Home loan interest deduction
        interest_ded = rental.home_loan_interest
        if rental.is_self_occupied:
            interest_ded = min(interest_ded, HOME_LOAN_INTEREST_SELF_OCCUPIED)
        
        taxable_rental = nav - standard_ded - interest_ded
        
        finding = Finding(
            guardian=self.guardian_type,
            code="RENTAL_SECTION_24",
            severity=Severity.INFO,
            category=Category.OPTIMIZATION,
            title="Rental Income with Section 24 Deduction",
            description=(
                f"Gross Rent: ₹{rental.gross_rent:,.0f} → "
                f"Taxable: ₹{taxable_rental:,.0f} after 30% standard deduction "
                f"(₹{standard_ded:,.0f})"
            ),
            action_steps=[
                f"NAV: ₹{nav:,.0f} (Gross - Municipal Taxes)",
                f"Standard Deduction (30%): ₹{standard_ded:,.0f}",
                f"Home Loan Interest: ₹{interest_ded:,.0f}",
                f"Net Taxable from House Property: ₹{taxable_rental:,.0f}",
            ],
            related_section="24",
        )
        
        return finding, taxable_rental
    
    def _process_gifts(self, gifts: list[GiftData]) -> tuple[list[Finding], float]:
        """
        Process gift income.
        Gifts from relatives: Exempt
        Gifts on marriage: Exempt
        Others > ₹50k: Fully taxable
        """
        findings = []
        taxable_gifts = 0.0
        non_relative_total = 0.0
        
        for gift in gifts:
            if gift.from_relative or gift.relation.lower() in RELATIVES:
                # Exempt from relative
                findings.append(Finding(
                    guardian=self.guardian_type,
                    code="GIFT_EXEMPT_RELATIVE",
                    severity=Severity.INFO,
                    category=Category.INFORMATION,
                    title="Gift from Relative - Exempt",
                    description=(
                        f"Gift of ₹{gift.amount:,.0f} from {gift.relation} is tax-free "
                        f"under Section 56(2)(x)."
                    ),
                    related_section="56(2)(x)",
                ))
            elif gift.occasion.lower() == "marriage":
                # Exempt on marriage
                findings.append(Finding(
                    guardian=self.guardian_type,
                    code="GIFT_EXEMPT_OCCASION",
                    severity=Severity.INFO,
                    category=Category.INFORMATION,
                    title="Wedding Gift - Exempt",
                    description=(
                        f"Gift of ₹{gift.amount:,.0f} received on marriage is tax-free."
                    ),
                    related_section="56(2)(x)",
                ))
            else:
                non_relative_total += gift.amount
        
        # Check non-relative threshold
        if non_relative_total > GIFT_EXEMPTION_NON_RELATIVE:
            taxable_gifts = non_relative_total  # Fully taxable if > ₹50k
            findings.append(Finding(
                guardian=self.guardian_type,
                code="GIFT_TAXABLE",
                severity=Severity.WARNING,
                category=Category.COMPLIANCE,
                title="Gift from Non-Relative - Taxable",
                description=(
                    f"Total gifts from non-relatives: ₹{non_relative_total:,.0f} exceeds "
                    f"₹{GIFT_EXEMPTION_NON_RELATIVE:,.0f} threshold. Entire amount is taxable."
                ),
                action_required=True,
                action_steps=[
                    "Report under 'Income from Other Sources'",
                    "Taxed at slab rate",
                    "Keep gift deed/proof for records",
                ],
                related_section="56(2)(x)",
            ))
        
        return findings, taxable_gifts
    
    def _check_huf_clubbing(self, huf: HUFData) -> Optional[Finding]:
        """
        Check Section 64(2) clubbing provisions.
        If HUF is funded from personal savings without consideration,
        income is clubbed back to the individual.
        """
        if huf.is_personal_transfer or "personal" in huf.fund_source.lower():
            return Finding(
                guardian=self.guardian_type,
                code="HUF_CLUBBING",
                severity=Severity.CRITICAL,
                category=Category.COMPLIANCE,
                title="HUF Clubbing - Section 64(2)",
                description=(
                    f"HUF income of ₹{huf.huf_income:,.0f} will be clubbed in YOUR income "
                    f"because HUF was funded from personal savings without adequate consideration."
                ),
                action_required=True,
                action_steps=[
                    "HUF income added to your total income",
                    "HUF still files separate return (showing Nil)",
                    "Future: Fund HUF from ancestral property or genuine gifts",
                ],
                related_section="64(2)",
            )
        
        return None


# Export
__all__ = ["WindfallWarden", "WindfallData", "RentalData", "GiftData", "HUFData"]

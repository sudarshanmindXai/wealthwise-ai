"""
WealthWise AI - Salary Sentinel
===============================
Agent 1: Analyzes salary income for optimization opportunities.

Responsibilities:
- HRA exemption calculation
- NPS 80CCD(2) optimization
- EV Lease arbitrage (Rule 3)
- Regime recommendation
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
    MAX_80CCD_2_RATE,
    HRA_METRO_RATE,
    HRA_NON_METRO_RATE,
    METRO_CITIES,
    STANDARD_DEDUCTION_NEW,
    STANDARD_DEDUCTION_OLD,
)


@dataclass
class SalaryData:
    """Input data for Salary Sentinel"""
    gross_salary: float
    basic_salary: float
    da: float = 0.0
    hra_received: float = 0.0
    employer_nps: float = 0.0
    rent_paid: float = 0.0
    city: str = ""
    is_metro: Optional[bool] = None
    
    @property
    def basic_plus_da(self) -> float:
        return self.basic_salary + self.da


class SalarySentinel(BaseGuardian):
    """
    The Salary Sentinel Guardian
    
    Optimizations:
    1. NPS Arbitrage - Validate 80CCD(2) utilization
    2. HRA Exemption - Calculate optimal HRA claim
    3. EV Lease - Recommend lease vs loan based on tax bracket
    """
    
    guardian_type = GuardianType.SALARY_SENTINEL
    
    def analyze(self, data: dict) -> GuardianResult:
        """Analyze salary data for optimization opportunities"""
        salary = self._parse_salary_data(data)
        findings = []
        
        # Check NPS 80CCD(2)
        nps_finding = self._check_nps_optimization(salary)
        if nps_finding:
            findings.append(nps_finding)
        
        # Check HRA
        hra_finding = self._check_hra_optimization(salary)
        if hra_finding:
            findings.append(hra_finding)
        
        # Check EV Lease opportunity
        ev_finding = self._check_ev_lease(salary)
        if ev_finding:
            findings.append(ev_finding)
        
        return GuardianResult(
            guardian=self.guardian_type,
            findings=findings,
            taxable_income_contribution=salary.gross_salary - STANDARD_DEDUCTION_NEW,
            metadata={
                "gross_salary": salary.gross_salary,
                "basic_plus_da": salary.basic_plus_da,
            }
        )
    
    def _parse_salary_data(self, data: dict) -> SalaryData:
        """Parse raw data into SalaryData"""
        salary_data = data.get("salary", data)
        
        city = salary_data.get("city", "")
        is_metro = salary_data.get("is_metro")
        if is_metro is None and city:
            is_metro = city.title() in METRO_CITIES
        
        return SalaryData(
            gross_salary=salary_data.get("gross_salary", salary_data.get("gross", 0)),
            basic_salary=salary_data.get("basic_salary", salary_data.get("basic", 0)),
            da=salary_data.get("da", 0),
            hra_received=salary_data.get("hra_received", salary_data.get("hra", 0)),
            employer_nps=salary_data.get("employer_nps_80ccd2", salary_data.get("employer_nps", 0)),
            rent_paid=salary_data.get("rent_paid", salary_data.get("rent_paid_annual", 0)),
            city=city,
            is_metro=is_metro,
        )
    
    def _check_nps_optimization(self, salary: SalaryData) -> Optional[Finding]:
        """
        Check if employer NPS contribution (80CCD(2)) is under-utilized.
        Max allowed: 14% of (Basic + DA) in New Regime.
        """
        max_allowed = salary.basic_plus_da * MAX_80CCD_2_RATE
        current = salary.employer_nps
        
        if current < max_allowed * 0.9:  # Less than 90% utilized
            gap = max_allowed - current
            # Estimate savings at 30% marginal rate
            potential_savings = gap * 0.30
            
            return Finding(
                guardian=self.guardian_type,
                code="NPS_UNDERUTILIZED",
                severity=Severity.WARNING,
                category=Category.OPTIMIZATION,
                title="NPS 80CCD(2) Under-Utilized",
                description=(
                    f"Your employer NPS contribution is ₹{current:,.0f}, but you can claim "
                    f"up to ₹{max_allowed:,.0f} (14% of Basic+DA). "
                    f"Gap: ₹{gap:,.0f}"
                ),
                potential_savings=potential_savings,
                action_required=True,
                action_steps=[
                    "Request HR to increase employer NPS contribution",
                    f"Maximum deductible: ₹{max_allowed:,.0f} under Sec 80CCD(2)",
                    "This deduction is allowed in BOTH Old and New regime",
                ],
                related_section="80CCD(2)",
            )
        
        return None
    
    def _check_hra_optimization(self, salary: SalaryData) -> Optional[Finding]:
        """
        Check HRA exemption opportunity (Old Regime only).
        HRA Exempt = Min(Actual HRA, Rent - 10% Basic, 50/40% Basic)
        """
        if salary.rent_paid <= 0 or salary.hra_received <= 0:
            return None
        
        # Calculate HRA exemption
        rate = HRA_METRO_RATE if salary.is_metro else HRA_NON_METRO_RATE
        
        houserent_minus_10pct = salary.rent_paid - (0.10 * salary.basic_plus_da)
        pct_of_basic = salary.basic_plus_da * rate
        
        hra_exempt = min(
            salary.hra_received,
            max(0, houserent_minus_10pct),
            pct_of_basic,
        )
        
        if hra_exempt > 0:
            # Estimate tax savings at 30% marginal rate
            potential_savings = hra_exempt * 0.30
            
            return Finding(
                guardian=self.guardian_type,
                code="HRA_UNCLAIMED",
                severity=Severity.INFO,
                category=Category.OPTIMIZATION,
                title="HRA Exemption Available (Old Regime)",
                description=(
                    f"You can claim HRA exemption of ₹{hra_exempt:,.0f} under the Old Regime. "
                    f"Rent paid: ₹{salary.rent_paid:,.0f}, HRA received: ₹{salary.hra_received:,.0f}"
                ),
                potential_savings=potential_savings,
                action_required=True,
                action_steps=[
                    "Collect rent receipts for the year",
                    f"Landlord PAN required if annual rent > ₹1,00,000",
                    "Submit Form 12BB to employer",
                ],
                related_section="10(13A)",
            )
        
        return None
    
    def _check_ev_lease(self, salary: SalaryData) -> Optional[Finding]:
        """
        Check EV Lease arbitrage opportunity.
        If marginal tax rate > 20%, EV lease is more tax efficient than loan.
        """
        # Only recommend if in higher tax bracket (>20L income)
        if salary.gross_salary < 2000000:
            return None
        
        return Finding(
            guardian=self.guardian_type,
            code="EV_LEASE_OPPORTUNITY",
            severity=Severity.INFO,
            category=Category.OPTIMIZATION,
            title="EV Lease Arbitrage Opportunity",
            description=(
                "At your income level, employer-provided EV lease has minimal perquisite "
                "value (Rule 3) compared to self-financed car loan. Consider restructuring."
            ),
            potential_savings=50000,  # Estimated annual benefit
            action_required=False,
            action_steps=[
                "Discuss EV lease benefit with HR",
                "Compare: Company lease (pre-tax) vs Personal loan (post-tax EMI)",
                "Rule 3 perquisite for EV is significantly lower",
            ],
            related_section="Rule 3",
        )


# Export
__all__ = ["SalarySentinel", "SalaryData"]

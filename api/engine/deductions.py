"""
WealthWise AI - Tax Deductions Calculator
==========================================
Calculates deductions under Chapter VI-A (80C, 80D, 80CCD, etc.)
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


# Deduction Limits (FY 2024-25)
LIMITS = {
    "80C": 150000,          # ELSS, PPF, LIC, Home Loan Principal, etc.
    "80CCC": 150000,        # Pension funds (combined with 80C)
    "80CCD_1": 150000,      # NPS employee contribution (combined with 80C)
    "80CCD_1B": 50000,      # Additional NPS (over and above 80C limit)
    "80CCD_2": None,        # Employer NPS contribution (10% of Basic+DA, no upper limit)
    "80D_SELF": 25000,      # Health insurance - self/family
    "80D_SELF_SENIOR": 50000,  # If self is senior citizen
    "80D_PARENTS": 25000,   # Health insurance - parents
    "80D_PARENTS_SENIOR": 50000,  # If parents are senior
    "80E": None,            # Education loan interest (no limit)
    "80EE": 50000,          # Home loan interest (first-time buyer, stamp < 45L)
    "80EEA": 150000,        # Affordable housing interest
    "80G": None,            # Donations (varies by type)
    "80GG": 60000,          # Rent paid (when no HRA)
    "80TTA": 10000,         # Savings account interest
    "80TTB": 50000,         # Senior citizen interest income
    "80U": 75000,           # Disability (125000 for severe)
}


@dataclass
class DeductionInput:
    """Input for deduction calculation"""
    # 80C components
    elss: float = 0
    ppf: float = 0
    lic: float = 0
    home_loan_principal: float = 0
    tuition_fees: float = 0
    nsc: float = 0
    sukanya_samriddhi: float = 0
    tax_saver_fd: float = 0
    other_80c: float = 0
    
    # 80CCD - NPS
    nps_employee: float = 0  # 80CCD(1) - within 80C limit
    nps_additional: float = 0  # 80CCD(1B) - additional 50k
    nps_employer: float = 0  # 80CCD(2) - 10% of Basic+DA
    basic_salary: float = 0  # For calculating 80CCD(2) limit
    
    # 80D - Health Insurance
    health_insurance_self: float = 0
    health_checkup_self: float = 0  # Max 5000 within 80D
    health_insurance_parents: float = 0
    health_checkup_parents: float = 0
    is_self_senior: bool = False
    is_parents_senior: bool = False
    
    # Other deductions
    education_loan_interest: float = 0  # 80E
    donations_80g: float = 0
    rent_paid_no_hra: float = 0  # 80GG
    savings_interest: float = 0  # 80TTA/80TTB
    is_senior_citizen: bool = False


@dataclass
class DeductionResult:
    """Result of deduction calculation"""
    section_80c: float = 0
    section_80ccd_1b: float = 0
    section_80ccd_2: float = 0
    section_80d: float = 0
    section_80e: float = 0
    section_80g: float = 0
    section_80gg: float = 0
    section_80tta_ttb: float = 0
    
    total_deductions: float = 0
    
    # Breakdown for transparency
    breakdown: Dict[str, float] = field(default_factory=dict)


def calculate_deductions(inp: DeductionInput) -> DeductionResult:
    """
    Calculate all Chapter VI-A deductions.
    
    Args:
        inp: DeductionInput with all investment/expense details
    
    Returns:
        DeductionResult with section-wise deductions
    """
    breakdown = {}
    
    # === Section 80C (Max 1.5L combined with 80CCC and 80CCD(1)) ===
    total_80c_eligible = (
        inp.elss + inp.ppf + inp.lic + inp.home_loan_principal +
        inp.tuition_fees + inp.nsc + inp.sukanya_samriddhi +
        inp.tax_saver_fd + inp.other_80c + inp.nps_employee
    )
    section_80c = min(total_80c_eligible, LIMITS["80C"])
    breakdown["80C_total_eligible"] = total_80c_eligible
    breakdown["80C_claimed"] = section_80c
    
    # === Section 80CCD(1B) - Additional NPS (Max 50k) ===
    section_80ccd_1b = min(inp.nps_additional, LIMITS["80CCD_1B"])
    breakdown["80CCD_1B"] = section_80ccd_1b
    
    # === Section 80CCD(2) - Employer NPS (10% of Basic+DA) ===
    max_employer_nps = inp.basic_salary * 0.10  # 10% for private sector
    section_80ccd_2 = min(inp.nps_employer, max_employer_nps)
    breakdown["80CCD_2"] = section_80ccd_2
    
    # === Section 80D - Health Insurance ===
    # Self/Family
    self_limit = LIMITS["80D_SELF_SENIOR"] if inp.is_self_senior else LIMITS["80D_SELF"]
    health_self = min(
        inp.health_insurance_self + min(inp.health_checkup_self, 5000),
        self_limit
    )
    
    # Parents
    parent_limit = LIMITS["80D_PARENTS_SENIOR"] if inp.is_parents_senior else LIMITS["80D_PARENTS"]
    health_parents = min(
        inp.health_insurance_parents + min(inp.health_checkup_parents, 5000),
        parent_limit
    )
    
    section_80d = health_self + health_parents
    breakdown["80D_self"] = health_self
    breakdown["80D_parents"] = health_parents
    
    # === Section 80E - Education Loan (No limit) ===
    section_80e = inp.education_loan_interest
    breakdown["80E"] = section_80e
    
    # === Section 80G - Donations (simplified, assuming 50% eligible) ===
    section_80g = inp.donations_80g * 0.5  # Conservative estimate
    breakdown["80G"] = section_80g
    
    # === Section 80GG - Rent (when no HRA) ===
    # Min of: 5000/month, 25% of total income, Rent - 10% of income
    # Simplified: just cap at 60k
    section_80gg = min(inp.rent_paid_no_hra, LIMITS["80GG"])
    breakdown["80GG"] = section_80gg
    
    # === Section 80TTA/80TTB - Savings Interest ===
    interest_limit = LIMITS["80TTB"] if inp.is_senior_citizen else LIMITS["80TTA"]
    section_80tta = min(inp.savings_interest, interest_limit)
    breakdown["80TTA_TTB"] = section_80tta
    
    # === Total ===
    total = (
        section_80c + section_80ccd_1b + section_80ccd_2 +
        section_80d + section_80e + section_80g + 
        section_80gg + section_80tta
    )
    
    return DeductionResult(
        section_80c=section_80c,
        section_80ccd_1b=section_80ccd_1b,
        section_80ccd_2=section_80ccd_2,
        section_80d=section_80d,
        section_80e=section_80e,
        section_80g=section_80g,
        section_80gg=section_80gg,
        section_80tta_ttb=section_80tta,
        total_deductions=total,
        breakdown=breakdown
    )

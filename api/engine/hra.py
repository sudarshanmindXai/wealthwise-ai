"""
WealthWise AI - HRA Exemption Calculator
=========================================
Calculates HRA (House Rent Allowance) exemption under Section 10(13A).

Exemption is the MINIMUM of:
1. Actual HRA received
2. 50% of Basic (metro) or 40% of Basic (non-metro)
3. Rent paid - 10% of Basic
"""

from dataclasses import dataclass
from .constants import METRO_CITIES, HRA_METRO_RATE, HRA_NON_METRO_RATE


@dataclass
class HRAResult:
    """Result of HRA exemption calculation"""
    hra_received: float
    basic_salary: float
    rent_paid: float
    city: str
    is_metro: bool
    
    # The three limits
    limit_actual_hra: float
    limit_percent_basic: float
    limit_rent_minus_10: float
    
    # Final exemption
    exemption: float
    taxable_hra: float


def calculate_hra_exemption(
    hra_received: float,
    basic_salary: float,
    rent_paid: float,
    city: str = "Other"
) -> HRAResult:
    """
    Calculate HRA exemption under Section 10(13A).
    
    Args:
        hra_received: Annual HRA received from employer
        basic_salary: Annual basic salary
        rent_paid: Annual rent paid for accommodation
        city: City of residence (for metro/non-metro determination)
    
    Returns:
        HRAResult with exemption details
    """
    is_metro = city.title() in METRO_CITIES
    
    # Three limits for HRA exemption
    limit_actual = hra_received
    limit_percent = basic_salary * (HRA_METRO_RATE if is_metro else HRA_NON_METRO_RATE)
    limit_rent = max(0, rent_paid - (0.10 * basic_salary))
    
    # Exemption is minimum of all three
    exemption = min(limit_actual, limit_percent, limit_rent)
    
    # Ensure non-negative
    exemption = max(0, exemption)
    
    # Taxable HRA is the remainder
    taxable_hra = max(0, hra_received - exemption)
    
    return HRAResult(
        hra_received=hra_received,
        basic_salary=basic_salary,
        rent_paid=rent_paid,
        city=city,
        is_metro=is_metro,
        limit_actual_hra=limit_actual,
        limit_percent_basic=limit_percent,
        limit_rent_minus_10=limit_rent,
        exemption=exemption,
        taxable_hra=taxable_hra
    )

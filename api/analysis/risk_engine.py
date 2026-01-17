"""
WealthWise AI - Tax Risk Engine
===============================
Analyzes financial data against income tax regulations to identify potential
scrutiny triggers and SFT (Statement of Financial Transactions) alerts.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RiskCategory(str, Enum):
    SFT = "SFT"         # Statement of Financial Transactions (High Value)
    AIS = "AIS"         # Annual Information Statement Mismatches
    COMPLIANCE = "Compliance"
    DEDUCTION = "Deduction"

class RiskAlert(BaseModel):
    title: str
    description: str
    level: RiskLevel
    category: RiskCategory
    impact_amount: Optional[float] = None
    section_ref: Optional[str] = None  # e.g. "Section 143(1)"

def analyze_risks(data: Dict) -> List[RiskAlert]:
    """
    Analyzes aggregated report data to identify tax risks.
    """
    alerts = []
    
    # Extract values safely
    gross_salary = data.get("gross_salary", 0)
    total_income = gross_salary + data.get("business_income", 0) + data.get("personal_income", 0)
    
    # --- 1. SFT High Value Transaction Checks ---
    
    # Credit Card Payments > ₹1L Cash or ₹10L Total
    # (Assuming we track this field, for now using a placeholder logic if we had expenses mapped)
    # Placeholder: In a real app, we'd sum up 'credit_card_payment' category from transactions
    
    # Savings Account Cash Deposits > ₹10 Lakh
    # We don't have explicit "cash deposit" tag yet, but high personal credits could trigger this
    personal_credits = data.get("personal_income", 0)
    if personal_credits > 1000000:
        alerts.append(RiskAlert(
            title="High Value Savings Transactions",
            description=f"Total credits in savings account (₹{personal_credits/100000:.1f}L) exceed the ₹10L SFT reporting threshold. Ensure these are explained sources.",
            level=RiskLevel.HIGH,
            category=RiskCategory.SFT,
            impact_amount=personal_credits
        ))

    # Business Turnover vs Presumptive Income (44ADA)
    business_income = data.get("business_income", 0)
    if business_income > 7500000: # 75L Limit for 44ADA (Updated from 50L)
        alerts.append(RiskAlert(
            title="Exceeds 44ADA Limit",
            description=f"Business receipts (₹{business_income/100000:.1f}L) exceed the ₹75L limit for presumptive taxation under Section 44ADA. Regular audit required.",
            level=RiskLevel.HIGH,
            category=RiskCategory.COMPLIANCE,
            section_ref="Section 44AB"
        ))
    
    # --- 2. Deduction & Exemption Checks ---
    
    # HRA Validation
    rent_paid = data.get("rent_paid", 0)
    if rent_paid > 100000 and not data.get("landlord_pan"):
        alerts.append(RiskAlert(
            title="HRA Claim without Landlord PAN",
            description="Rent paid exceeds ₹1 Lakh/year. Mandatory to report Landlord's PAN to avoid disallowance.",
            level=RiskLevel.MEDIUM,
            category=RiskCategory.DEDUCTION,
            section_ref="Section 10(13A)"
        ))
        
    # Fake Donation (80G) Warning
    donation_80g = data.get("deduction_80g", 0)
    if donation_80g > 0:
        alerts.append(RiskAlert(
            title="80G Donation Scrutiny",
            description="Ensure you have a valid receipt with donation ID. AI validates only documented claims.",
            level=RiskLevel.LOW,
            category=RiskCategory.DEDUCTION,
            section_ref="Section 80G"
        ))

    # --- 3. AIS/TIS Mismatches (Simulated) ---
    
    # Unreported Interest (Common Issue)
    # Heuristic: If we see no interest income but high balance or salary
    interest_income = 0 # Placeholder for extracted interest
    if interest_income == 0 and gross_salary > 1000000:
        alerts.append(RiskAlert(
            title="Possible Missed Savings Interest",
            description="No savings interest income reported. AIS almost always captures interest from savings accounts.",
            level=RiskLevel.LOW,
            category=RiskCategory.AIS
        ))
        
    # --- 4. Logic Constraints ---
    
    # Standard Deduction Double Claim (Job Switcher)
    # Hard to detect without multiple Form 16s, but if employer_name count > 1 (future feature)
    
    return alerts

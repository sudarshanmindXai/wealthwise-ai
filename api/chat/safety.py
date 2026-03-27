"""
WealthWise AI - Chat Engine Safety Layer
==========================================
Filters for PII, compliance, and harmful requests.
"""

import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class SafetyViolationType(str, Enum):
    """Types of safety violations"""
    EVASION = "tax_evasion"
    PII_EXPOSURE = "pii_exposure"
    HARMFUL_ADVICE = "harmful_advice"
    NONE = "none"


# Red line phrases that require automatic refusal
RED_LINE_PHRASES = [
    r"hide\s+(income|money|cash)",
    r"evade\s+tax",
    r"black\s*money",
    r"don'?t\s+report",
    r"fake\s+(receipt|invoice|bill)",
    r"benami",
    r"cash\s+transaction.*hide",
    r"not\s+declare",
    r"avoid\s+detection",
    r"under\s*the\s*table",
]

# Compile patterns for efficiency
RED_LINE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in RED_LINE_PHRASES]

# PII patterns to redact from logs/responses
PII_PATTERNS = {
    "pan": re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]", re.IGNORECASE),
    "aadhaar": re.compile(r"\d{4}\s?\d{4}\s?\d{4}"),
    "bank_account": re.compile(r"\d{9,18}"),
    "phone": re.compile(r"[+]?91[-\s]?\d{10}"),
}


@dataclass
class SafetyCheckResult:
    """Result of safety check"""
    is_safe: bool
    violation_type: SafetyViolationType
    message: Optional[str] = None
    redacted_text: Optional[str] = None


EVASION_REFUSAL = """I cannot provide guidance on non-compliant activities. Tax evasion is a criminal offense under Section 276C of the Income Tax Act.

Would you like to explore **legal** ways to optimize your tax liability instead? I can help with:
- Section 80C/80D deductions
- HRA exemption calculation
- Presumptive taxation (44ADA)
- NPS employer contribution benefits"""


def check_message_safety(message: str) -> SafetyCheckResult:
    """
    Check if user message contains red line content.
    
    Returns:
        SafetyCheckResult with violation type and suggested response
    """
    message_lower = message.lower()
    
    # Check for red line phrases
    for pattern in RED_LINE_PATTERNS:
        if pattern.search(message_lower):
            return SafetyCheckResult(
                is_safe=False,
                violation_type=SafetyViolationType.EVASION,
                message=EVASION_REFUSAL,
            )
    
    return SafetyCheckResult(
        is_safe=True,
        violation_type=SafetyViolationType.NONE,
    )


def redact_pii(text: str) -> str:
    """
    Redact PII from text before logging or external API calls.
    """
    result = text
    
    for pii_type, pattern in PII_PATTERNS.items():
        if pii_type == "pan":
            result = pattern.sub("[PAN_REDACTED]", result)
        elif pii_type == "aadhaar":
            result = pattern.sub("[AADHAAR_REDACTED]", result)
        elif pii_type == "bank_account":
            result = pattern.sub("[ACCOUNT_REDACTED]", result)
        elif pii_type == "phone":
            result = pattern.sub("[PHONE_REDACTED]", result)
    
    return result


def validate_response_citations(response: str) -> bool:
    """
    Check if response contains proper section citations.
    Warn if making claims without citations.
    """
    # Look for section references
    section_pattern = re.compile(r"[Ss]ection\s+\d+[A-Z]*|\b\d+[A-Z]{1,3}\b", re.IGNORECASE)
    
    # Claims that should have citations
    claim_phrases = [
        "you can claim", "you are eligible", "the limit is",
        "tax rate is", "deduction of", "exemption of"
    ]
    
    has_claim = any(phrase in response.lower() for phrase in claim_phrases)
    has_citation = bool(section_pattern.search(response))
    
    # If making a claim, should have citation
    if has_claim and not has_citation:
        return False
    
    return True


def sanitize_for_llm(user_context: dict) -> dict:
    """
    Sanitize user context before sending to LLM.
    Remove sensitive fields that shouldn't go to external API.
    """
    safe_context = {}
    
    # Fields safe to include
    safe_fields = [
        "gross_salary", "basic_salary", "hra_received",
        "rent_paid", "freelance_receipts", "ltcg", "stcg",
        "deductions", "tax_old", "tax_new", "findings",
        "city", "regime_recommended"
    ]
    
    for key, value in user_context.items():
        if key in safe_fields:
            safe_context[key] = value
        elif key in ["pan", "aadhaar", "bank_account"]:
            # Skip PII entirely
            continue
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            safe_context[key] = sanitize_for_llm(value)
    
    return safe_context


# Export
__all__ = [
    "check_message_safety",
    "redact_pii", 
    "validate_response_citations",
    "sanitize_for_llm",
    "SafetyCheckResult",
    "SafetyViolationType",
]

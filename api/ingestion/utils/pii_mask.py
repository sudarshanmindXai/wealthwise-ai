import re
from typing import Optional

class PIIScrubber:
    """
    Utility to mask Personally Identifiable Information (PII) 
    from text before storage or logging.
    """
    
    PATTERNS = {
        "pan": r"[A-Z]{5}[0-9]{4}[A-Z]",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
        "aadhaar": r"\b\d{4}\s\d{4}\s\d{4}\b",
        "ifsc": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        "account": r"\b\d{11,18}\b",  # Indian bank account numbers are typically 11-18 digits. 9-10 digits might clash with phone.
    }
    
    # Patterns for masking names in transaction descriptions
    NAME_PATTERNS = [
        # "FOR NAME" pattern (FD BKD FOR SIDDHANT JHA, PAYMENT FOR JOHN DOE)
        (r"(FOR\s+)([A-Z][A-Z\s]{2,30})(\s|$|[-/])", r"\1[REDACTED]\3"),
        # Trailing "-NAME" at end (XXXX1330 -SIDDHANT JHA)
        (r"(\s[-])([A-Z][A-Z\s]{2,30})($)", r"\1[REDACTED]\3"),
        # UPI: "UPI-JOHN DOE-bank@upi" or "UPI/DR/123/JOHN DOE/bank"
        (r"(UPI[-/][A-Z0-9/]+[-/])([A-Z][A-Za-z\s\.]+?)(-[a-z@])", r"\1[REDACTED]\3"),
        # UPI simpler: "UPI-NAME-" pattern
        (r"(UPI[-/])([A-Z][A-Za-z\s\.]{2,30})([-/])", r"\1[REDACTED]\3"),
        # NEFT/RTGS/IMPS to NAME
        (r"((?:NEFT|RTGS|IMPS|TRANSFER)\s*(?:TO|FROM|CR|DR)?[\s:]+)([A-Z][A-Za-z\s\.]{2,40})(\s|$|/)", r"\1[REDACTED]\3"),
        # "Transfer to/from NAME"
        (r"(Transfer\s+(?:to|from)\s+)([A-Z][A-Za-z\s\.]{2,40})(\s|$)", r"\1[REDACTED]\3"),
        # "MR/MRS/MS NAME" patterns
        (r"\b(MR\.?|MRS\.?|MS\.?|SHRI|SMT)\s+([A-Z][A-Za-z\s\.]{2,40})(\s|$)", r"\1 [REDACTED]\3"),
        # "BY-NAME" or "TO-NAME" common in statements
        (r"(BY[-\s]|TO[-\s])([A-Z][A-Za-z\s]{3,30})(\s|$|/)", r"\1[REDACTED]\3"),
    ]
    
    @staticmethod
    def mask_pan(text: str) -> str:
        """Mask PAN: ABCDE1234F -> XXXXX1234X"""
        def replace(match):
            pan = match.group(0)
            return "X" * 5 + pan[5:9] + "X"
        return re.sub(PIIScrubber.PATTERNS["pan"], replace, text)

    @staticmethod
    def mask_email(text: str) -> str:
        """Mask Email: user@example.com -> u***@example.com"""
        def replace(match):
            email = match.group(0)
            user, domain = email.split('@')
            masked_user = user[:1] + "***" if len(user) > 1 else "***"
            return f"{masked_user}@{domain}"
        return re.sub(PIIScrubber.PATTERNS["email"], replace, text, flags=re.IGNORECASE)

    @staticmethod
    def mask_ifsc(text: str) -> str:
        """Mask IFSC: HDFC0001234 -> HDFC0XXXXXX"""
        def replace(match):
            ifsc = match.group(0)
            return ifsc[:5] + "X" * 6
        return re.sub(PIIScrubber.PATTERNS["ifsc"], replace, text)

    @staticmethod
    def mask_account(text: str) -> str:
        """Mask Account Number: 12345678901 -> XXXXXXX8901"""
        def replace(match):
            acc = match.group(0)
            if len(acc) <= 4:
                return "X" * len(acc)
            return "X" * (len(acc) - 4) + acc[-4:]
        return re.sub(PIIScrubber.PATTERNS["account"], replace, text)

    @staticmethod
    def mask_phone(text: str) -> str:
        """Mask Phone: 9876543210 -> XXXXXXXXXX"""
        return re.sub(PIIScrubber.PATTERNS["phone"], "XXXXXXXXXX", text)

    @staticmethod
    def mask_names(text: str) -> str:
        """Mask personal names in transaction descriptions"""
        if not text:
            return text
        result = text
        for pattern, replacement in PIIScrubber.NAME_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result

    @staticmethod
    def scrub_text(text: str) -> str:
        """Run all scrubbers on text"""
        if not text:
            return text
        text = PIIScrubber.mask_pan(text)
        text = PIIScrubber.mask_email(text)
        text = PIIScrubber.mask_ifsc(text)
        text = PIIScrubber.mask_account(text)
        text = PIIScrubber.mask_phone(text)
        text = PIIScrubber.mask_names(text)
        return text


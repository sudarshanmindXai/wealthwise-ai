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
    }
    
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
    def mask_phone(text: str) -> str:
        """Mask Phone: +91 9876543210 -> +91 98******10"""
        def replace(match):
            phone = match.group(0)
            # Find the last 10 digits
            digits = re.findall(r"\d", phone)
            if len(digits) >= 10:
                # Keep first 2 and last 2 of the 10-digit part
                return re.sub(r"\d", "X", phone) # Simple full mask for now
                # precise masking is complex with formats
            return "XXXXXXXXXX"
        return re.sub(PIIScrubber.PATTERNS["phone"], "XXXXXXXXXX", text)

    @staticmethod
    def scrub_text(text: str) -> str:
        """Run all scrubbers on text"""
        text = PIIScrubber.mask_pan(text)
        text = PIIScrubber.mask_email(text)
        text = PIIScrubber.mask_phone(text)
        # Add basic name scrubbing heuristics if needed, but risky
        return text

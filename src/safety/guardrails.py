from typing import Dict, Any


ALLOWED_DOMAIN_KEYWORDS = [
    "tax", "itr", "income", "deduction",
    "regime", "salary", "assessment year",
    "section", "act", "return"
]


class SafetyViolation(Exception):
    pass


def check_domain(user_message: str):
    """
    Ensures the query is tax-domain only.
    """
    msg = user_message.lower()

    if not any(keyword in msg for keyword in ALLOWED_DOMAIN_KEYWORDS):
        raise SafetyViolation(
            "This system only answers Indian income tax related questions."
        )


def enforce_no_advice_language(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a safety disclaimer to all responses.
    """
    response["disclaimer"] = (
        "This is an informational system based on provided inputs. "
        "It is not professional tax advice."
    )
    return response
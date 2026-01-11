from enum import Enum
from typing import Dict, Any

from src.core.recommendation_service import get_tax_recommendation


class AgentIntent(str, Enum):
    TAX_RECOMMENDATION = "tax_recommendation"
    EXPLANATION = "explanation"
    MISSING_INFO = "missing_info"
    CITATIONS = "citations"


def classify_intent(user_query: str) -> AgentIntent:
    """
    Very simple deterministic intent classifier.
    LLM will replace this later.
    """
    q = user_query.lower()

    if "itr" in q or "file" in q or "regime" in q:
        return AgentIntent.TAX_RECOMMENDATION

    if "why" in q or "explain" in q:
        return AgentIntent.EXPLANATION

    if "missing" in q or "need" in q:
        return AgentIntent.MISSING_INFO

    if "law" in q or "section" in q or "citation" in q:
        return AgentIntent.CITATIONS

    return AgentIntent.TAX_RECOMMENDATION


def agent_route(
    user_query: str,
    profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Routes the user request to the correct deterministic capability.
    """

    intent = classify_intent(user_query)

    # For Phase 2, everything routes through the same core
    result = get_tax_recommendation(profile)

    if intent == AgentIntent.EXPLANATION:
        return {
            "intent": intent,
            "explanation": result["explanation"]
        }

    if intent == AgentIntent.MISSING_INFO:
        return {
            "intent": intent,
            "missing_info": result["missing_info"],
            "followup_questions": result["followup_questions"]
        }

    if intent == AgentIntent.CITATIONS:
        return {
            "intent": intent,
            "citations": result["citations"]
        }

    # Default: full recommendation
    return {
        "intent": intent,
        "recommendation": result
    }
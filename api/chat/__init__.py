"""
WealthWise AI - Chat Engine
"""

from .agent import CACompanionAgent, create_agent
from .memory import ChatMemory, UserContext, Message
from .safety import check_message_safety, redact_pii, SafetyCheckResult
from .tools import recalculate_tax, calculate_hra_exemption, search_tax_law, TOOL_DEFINITIONS

__all__ = [
    "CACompanionAgent",
    "create_agent",
    "ChatMemory",
    "UserContext",
    "Message",
    "check_message_safety",
    "redact_pii",
    "SafetyCheckResult",
    "recalculate_tax",
    "calculate_hra_exemption",
    "search_tax_law",
    "TOOL_DEFINITIONS",
]

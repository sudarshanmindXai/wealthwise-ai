"""
WealthWise AI - Chat Memory Manager
====================================
Manages conversation history and user context.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import json


@dataclass
class Message:
    """Single chat message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class UserContext:
    """User's financial context for the chat session"""
    # Calculated values
    gross_income: float = 0.0
    taxable_income_old: float = 0.0
    taxable_income_new: float = 0.0
    tax_old: float = 0.0
    tax_new: float = 0.0
    recommended_regime: str = "new"
    
    # Guardian findings
    findings: list[dict] = field(default_factory=list)
    potential_savings: float = 0.0
    
    # Input data summary
    salary_summary: Optional[dict] = None
    freelance_summary: Optional[dict] = None
    investment_summary: Optional[dict] = None
    
    def to_context_string(self) -> str:
        """Convert to string for LLM context injection"""
        return f"""
## User's Financial Summary (FY 2025-26)

**Income:**
- Gross Income: ₹{self.gross_income:,.0f}
- Taxable (Old Regime): ₹{self.taxable_income_old:,.0f}
- Taxable (New Regime): ₹{self.taxable_income_new:,.0f}

**Tax Liability:**
- Old Regime Tax: ₹{self.tax_old:,.0f}
- New Regime Tax: ₹{self.tax_new:,.0f}
- Recommended: {self.recommended_regime.upper()} Regime

**Optimization Findings:**
{self._format_findings()}

**Potential Savings: ₹{self.potential_savings:,.0f}**
"""
    
    def _format_findings(self) -> str:
        if not self.findings:
            return "- No optimization findings yet."
        
        lines = []
        for f in self.findings[:5]:  # Limit to top 5
            savings = f.get("potential_savings", 0)
            savings_str = f" (₹{savings:,.0f})" if savings > 0 else ""
            lines.append(f"- [{f.get('guardian', 'unknown')}] {f.get('title', 'Finding')}{savings_str}")
        
        return "\n".join(lines)


class ChatMemory:
    """
    Manages conversation history with sliding window.
    Keeps last N turns for context.
    """
    
    def __init__(self, max_turns: int = 10, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.max_turns = max_turns
        self.messages: list[Message] = []
        self.user_context: Optional[UserContext] = None
        self.created_at = datetime.now()
    
    @staticmethod
    def _generate_session_id() -> str:
        from uuid import uuid4
        return str(uuid4())[:8]
    
    def add_message(self, role: str, content: str, metadata: Optional[dict] = None):
        """Add message to history"""
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(msg)
        
        # Trim to max turns (each turn = user + assistant)
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            # Keep system messages + last N turns
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            self.messages = system_msgs + other_msgs[-max_messages:]
    
    def set_context(self, context: UserContext):
        """Set user financial context"""
        self.user_context = context
    
    def get_messages_for_llm(self) -> list[dict]:
        """Get messages formatted for LLM API"""
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
        ]
    
    def get_last_n_messages(self, n: int = 5) -> list[Message]:
        """Get last N messages"""
        return self.messages[-n:]
    
    def clear(self):
        """Clear conversation history (keep system prompt)"""
        system_msgs = [m for m in self.messages if m.role == "system"]
        self.messages = system_msgs
    
    def to_dict(self) -> dict:
        """Serialize for storage"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in self.messages
            ],
            "user_context": {
                "gross_income": self.user_context.gross_income,
                "tax_old": self.user_context.tax_old,
                "tax_new": self.user_context.tax_new,
            } if self.user_context else None,
        }


# Export
__all__ = ["ChatMemory", "Message", "UserContext"]

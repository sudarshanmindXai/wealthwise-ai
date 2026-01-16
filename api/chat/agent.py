"""
WealthWise AI - Chat Agent
===========================
The main CA Companion agent with RAG and tool access.
"""

from typing import Optional, AsyncGenerator
from pathlib import Path

from .memory import ChatMemory, UserContext, Message
from .safety import check_message_safety, redact_pii, sanitize_for_llm
from .tools import (
    recalculate_tax,
    calculate_hra_exemption, 
    search_tax_law,
    TOOL_DEFINITIONS,
)


# Load system prompt
PROMPT_PATH = Path(__file__).parent.parent.parent.parent.parent / "holy_grail" / "chatbot_sys_prompt.md"


def load_system_prompt() -> str:
    """Load the system prompt from file"""
    if PROMPT_PATH.exists():
        with open(PROMPT_PATH, "r") as f:
            return f.read()
    
    # Fallback minimal prompt
    return """You are WealthWise, an AI Tax Assistant for Indian Income Tax (FY 2025-26).
    
Rules:
1. Always cite Section numbers when making claims
2. Never advise on tax evasion
3. If unsure, recommend consulting a CA
4. Use the user's actual data from the context provided"""


class CACompanionAgent:
    """
    The CA Companion Chatbot Agent.
    
    Features:
    - Context-aware (knows user's report data)
    - RAG-powered (can search legal docs)
    - Tool-equipped (can recalculate tax)
    - Safety-first (refuses evasion queries)
    """
    
    def __init__(
        self,
        user_context: Optional[UserContext] = None,
        session_id: Optional[str] = None,
    ):
        self.memory = ChatMemory(max_turns=10, session_id=session_id)
        
        # Set user context
        if user_context:
            self.memory.set_context(user_context)
        
        # Initialize with system prompt
        system_prompt = load_system_prompt()
        self.memory.add_message("system", system_prompt)
        
        # Add context if available
        if user_context:
            context_str = user_context.to_context_string()
            self.memory.add_message("system", f"USER CONTEXT:\n{context_str}")
    
    def set_context(self, context: UserContext):
        """Update user context mid-conversation"""
        self.memory.set_context(context)
        context_str = context.to_context_string()
        self.memory.add_message("system", f"UPDATED CONTEXT:\n{context_str}")
    
    async def chat(self, user_message: str) -> str:
        """
        Process user message and return response.
        
        Args:
            user_message: User's question
        
        Returns:
            Assistant's response (with citations)
        """
        # Step 1: Safety check
        safety_result = check_message_safety(user_message)
        if not safety_result.is_safe:
            self.memory.add_message("user", user_message)
            self.memory.add_message("assistant", safety_result.message)
            return safety_result.message
        
        # Step 2: Add to memory
        self.memory.add_message("user", user_message)
        
        # Step 3: Detect if tool call needed
        tool_result = self._check_for_tool_call(user_message)
        tool_context = ""
        if tool_result:
            tool_context = f"\n\nTOOL RESULT:\n{tool_result}"
        
        # Step 4: Generate response (placeholder - needs LLM integration)
        response = self._generate_response(user_message, tool_context)
        
        # Step 5: Add response to memory
        self.memory.add_message("assistant", response)
        
        return response
    
    def _check_for_tool_call(self, message: str) -> Optional[str]:
        """Detect if message requires tool call and execute"""
        message_lower = message.lower()
        
        # Check for "What If" scenarios
        if any(phrase in message_lower for phrase in ["what if", "if i", "suppose"]):
            if "rent" in message_lower or "hra" in message_lower:
                # Try to extract rent value and calculate
                if self.memory.user_context:
                    result = calculate_hra_exemption(
                        basic_salary=self.memory.user_context.salary_summary.get("basic", 0) if self.memory.user_context.salary_summary else 0,
                        hra_received=self.memory.user_context.salary_summary.get("hra", 0) if self.memory.user_context.salary_summary else 0,
                        rent_paid_monthly=25000,  # Example value
                        is_metro=True,
                    )
                    return result.message
            
            if "nps" in message_lower:
                if self.memory.user_context:
                    result = recalculate_tax(
                        gross_salary=self.memory.user_context.gross_income,
                        employer_nps=self.memory.user_context.gross_income * 0.14,
                    )
                    return result.message
        
        # Check for section lookup
        if "section" in message_lower or "what does" in message_lower:
            result = search_tax_law(message)
            if result.success and result.data.get("results"):
                return f"Found: {result.data['results'][0].get('text', '')[:300]}..."
        
        return None
    
    def _generate_response(self, user_message: str, tool_context: str = "") -> str:
        """
        Generate response using LLM.
        
        Note: This is a placeholder. In production, this would call
        OpenAI/Anthropic API with the conversation history.
        """
        # For demo, provide rule-based responses
        message_lower = user_message.lower()
        
        if "hra" in message_lower:
            return f"""Your HRA exemption is calculated under **Section 10(13A)**.

The exemption is the **minimum** of:
1. Actual HRA received from employer
2. Rent paid - 10% of Basic salary
3. 50% of Basic (Metro) or 40% (Non-Metro)

{tool_context if tool_context else ''}

**Action:** To maximize HRA, either increase rent or ask HR to restructure more salary into HRA component."""

        if "nps" in message_lower or "80ccd" in message_lower:
            return f"""NPS contributions have two deductions available:

1. **Section 80CCD(1)**: Your contribution (up to ₹1.5L, within 80C limit)
2. **Section 80CCD(1B)**: Additional ₹50,000 over 80C limit
3. **Section 80CCD(2)**: Employer contribution (up to 14% of Basic+DA)

The **employer contribution is allowed in BOTH regimes** - this is the key optimization.

{tool_context if tool_context else ''}

**Action:** Request HR to increase employer NPS contribution to 14% of Basic."""

        if "crypto" in message_lower or "115bbh" in message_lower:
            return """Crypto/VDA taxation is governed by **Section 115BBH** (introduced in Finance Act 2022).

**Key Rules:**
- Flat 30% tax on gains (no slab benefit)
- No set-off of losses against any income
- Cannot carry forward losses
- 1% TDS on transfers (Section 194S)

⚠️ **Warning:** Your crypto loss of ₹20,000 is a "dead loss" - it cannot reduce your tax liability.

**Action:** Factor this into future investment decisions. Consider regular equities for tax-efficient gains."""

        if "44ada" in message_lower or "presumptive" in message_lower:
            return """**Section 44ADA** allows professionals to declare 50% of gross receipts as profit.

**Eligibility:**
- Specified professionals (legal, medical, engineering, etc.)
- Gross receipts ≤ ₹75L (if cash < 5%) or ≤ ₹50L otherwise

**Benefits:**
- No need to maintain books of account
- No audit required (if profit ≥ 50%)
- Simpler ITR-4 filing

**Your Status:** You qualify for 44ADA with taxable income of ₹3,00,000 (50% of ₹6,00,000).

**Action:** File ITR-4 for presumptive income."""

        # Default response
        return f"""Thank you for your question about: *"{user_message}"*

Based on your financial profile, I can help you understand the tax implications.

{tool_context if tool_context else 'Let me search the relevant sections...'}

Could you please clarify which specific aspect you'd like me to explain? For example:
- The calculation logic
- Optimization opportunities
- Required documentation

*Note: I cite relevant sections of the Income Tax Act to ensure accuracy.*"""
    
    def get_session_summary(self) -> dict:
        """Get summary of the chat session"""
        return self.memory.to_dict()


# Factory function
def create_agent(user_context: Optional[dict] = None) -> CACompanionAgent:
    """Create a new chat agent with optional context"""
    ctx = None
    if user_context:
        ctx = UserContext(
            gross_income=user_context.get("gross_income", 0),
            tax_old=user_context.get("tax_old", 0),
            tax_new=user_context.get("tax_new", 0),
            recommended_regime=user_context.get("recommended", "new"),
            findings=user_context.get("findings", []),
            potential_savings=user_context.get("potential_savings", 0),
        )
    
    return CACompanionAgent(user_context=ctx)


# Export
__all__ = ["CACompanionAgent", "create_agent", "load_system_prompt"]

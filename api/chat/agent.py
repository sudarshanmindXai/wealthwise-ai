"""
WealthWise AI - Chat Agent
===========================
The main CA Companion agent with RAG and tool access.
"""

import os
import json
from typing import Optional, AsyncGenerator, Dict, Any, List
from pathlib import Path

from openai import AsyncOpenAI
from dotenv import load_dotenv

from .memory import ChatMemory, UserContext, Message
from .safety import check_message_safety, redact_pii, sanitize_for_llm
from .tools import (
    recalculate_tax,
    calculate_hra_exemption, 
    search_tax_law,
    TOOL_DEFINITIONS,
)

# Load env from explicit path
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


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
        
        # Initialize OpenAI Client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found. Chat will fail.")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

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
        Process user message and return response using OpenAI with tools.
        """
        # Step 1: Safety check
        safety_result = check_message_safety(user_message)
        if not safety_result.is_safe:
            self.memory.add_message("user", user_message)
            self.memory.add_message("assistant", safety_result.message)
            return safety_result.message
        
        # Step 2: Add to memory
        self.memory.add_message("user", user_message)
        
        # Step 3: Generate response with tool loop
        try:
            response = await self._generate_response()
        except Exception as e:
            print(f"Error generating response: {e}")
            response = "I apologize, but I encountered an error while processing your request. Please try again."
        
        # Step 4: Add response to memory
        self.memory.add_message("assistant", response)
        
        return response
    
    async def _generate_response(self) -> str:
        """Generate response using OpenAI with tool calling loop."""
        
        # Prepare messages
        messages = self._prepare_messages()
        
        # Tool mapping
        available_tools = {
            "recalculate_tax": recalculate_tax,
            "calculate_hra_exemption": calculate_hra_exemption,
            "search_tax_law": search_tax_law,
        }
        
        # First call to LLM
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": t} for t in TOOL_DEFINITIONS],
            tool_choice="auto", 
        )
        
        response_msg = response.choices[0].message
        
        # Check for tool calls
        if response_msg.tool_calls:
            # Add the assistant's request to valid messages
            messages.append(response_msg)
            
            # Process map
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                print(f"Defining tool call: {func_name} with {func_args}")
                
                if func_name in available_tools:
                    tool_function = available_tools[func_name]
                    # Call the tool
                    try:
                        result = tool_function(**func_args)
                        content = json.dumps(result.data) if result.success else f"Error: {result.message}"
                    except Exception as e:
                        content = f"Tool execution failed: {str(e)}"
                        
                    # Add tool response
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": content,
                    })
            
            # Second call to LLM with tool outputs
            second_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return second_response.choices[0].message.content
            
        return response_msg.content

    def _prepare_messages(self) -> List[Dict[str, Any]]:
        """Convert memory to OpenAI message format."""
        openai_messages = []
        
        # System prompt with context is already in memory[0] if set correctly
        # But let's map strictly
        
        for msg in self.memory.messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
            
        return openai_messages
    
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

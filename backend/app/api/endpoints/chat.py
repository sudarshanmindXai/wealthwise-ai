"""
WealthWise AI - Chat Endpoint
==============================
API endpoint for the CA Companion chatbot.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ...chat_engine import create_agent, check_message_safety, UserContext


router = APIRouter()


# Session storage (in production, use Redis)
_sessions: dict[str, any] = {}


class ChatRequest(BaseModel):
    """Chat request body"""
    message: str
    session_id: Optional[str] = None
    user_context: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Why is my HRA exemption only ₹20,000?",
                "session_id": "abc123",
                "user_context": {
                    "gross_income": 1800000,
                    "tax_old": 245000,
                    "tax_new": 265000,
                    "recommended": "old",
                    "potential_savings": 127800,
                }
            }
        }


class ChatResponse(BaseModel):
    """Chat response body"""
    response: str
    session_id: str
    is_safe: bool = True
    tool_used: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the CA Companion.
    
    The chatbot:
    - Uses user's financial context if provided
    - Refuses to help with tax evasion
    - Cites relevant IT Act sections
    - Can recalculate tax for "What If" scenarios
    """
    try:
        # Safety check first
        safety_result = check_message_safety(request.message)
        if not safety_result.is_safe:
            return ChatResponse(
                response=safety_result.message,
                session_id=request.session_id or "new",
                is_safe=False,
            )
        
        # Get or create agent
        session_id = request.session_id
        if session_id and session_id in _sessions:
            agent = _sessions[session_id]
            # Update context if provided
            if request.user_context:
                ctx = UserContext(
                    gross_income=request.user_context.get("gross_income", 0),
                    tax_old=request.user_context.get("tax_old", 0),
                    tax_new=request.user_context.get("tax_new", 0),
                    recommended_regime=request.user_context.get("recommended", "new"),
                    findings=request.user_context.get("findings", []),
                    potential_savings=request.user_context.get("potential_savings", 0),
                )
                agent.set_context(ctx)
        else:
            agent = create_agent(request.user_context)
            session_id = agent.memory.session_id
            _sessions[session_id] = agent
        
        # Get response
        response = await agent.chat(request.message)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            is_safe=True,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session"""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"message": "Session cleared"}
    return {"message": "Session not found"}


@router.get("/chat/{session_id}/history")
async def get_history(session_id: str):
    """Get chat history for a session"""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = _sessions[session_id]
    return agent.get_session_summary()

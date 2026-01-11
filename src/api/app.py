from fastapi import FastAPI, HTTPException

# Schemas
from src.api.schemas.chat import ChatRequest
from src.api.schemas.request import TaxProfile
from src.api.schemas.response import TaxRecommendationResponse

# Core logic
from src.core.recommendation_service import get_tax_recommendation
from src.agent.router import agent_route

# Conversation
from src.conversation.memory import ConversationMemory

# Safety guardrails
from src.safety.guardrails import (
    check_domain,
    enforce_no_advice_language,
    SafetyViolation
)

app = FastAPI(
    title="WealthWise-AI",
    description="Deterministic tax recommendation API (India)",
    version="1.0.0"
)

memory = ConversationMemory(max_turns=5)

@app.post(
    "/tax/recommendation",
    response_model=TaxRecommendationResponse
)
def tax_recommendation(profile: TaxProfile):
    try:
        return get_tax_recommendation(profile.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tax/chat")
def tax_chat(request: ChatRequest):
    try:
        check_domain(request.user_message)

        response = agent_route(
            user_query=request.user_message,
            profile=request.profile
        )

        response = enforce_no_advice_language(response)
        return response

    except SafetyViolation as sv:
        raise HTTPException(status_code=400, detail=str(sv))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
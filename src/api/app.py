from fastapi import FastAPI, HTTPException, Request

from src.api.schemas.chat import ChatRequest
from src.api.schemas.request import TaxProfile
from src.api.schemas.response import TaxRecommendationResponse

from src.core.recommendation_service import get_tax_recommendation
from src.agent.router import agent_route
from src.conversation.memory import ConversationMemory
from src.safety.guardrails import check_domain, enforce_no_advice_language, SafetyViolation

from src.core.logging_config import setup_logging
from src.core.request_logging_middleware import RequestLoggingMiddleware

setup_logging(level="INFO")

app = FastAPI(
    title="WealthWise-AI",
    description="Deterministic tax recommendation API (India)",
    version="1.0.0"
)

app.add_middleware(RequestLoggingMiddleware)

memory = ConversationMemory(max_turns=5)

@app.post(
    "/tax/recommendation",
    response_model=TaxRecommendationResponse
)
def tax_recommendation(profile: TaxProfile, request: Request):
    try:
        return get_tax_recommendation(
            {**profile.dict(), "_request_id": request.state.request_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tax/chat")
def tax_chat(request_body: ChatRequest, request: Request):
    try:
        check_domain(request_body.user_message)

        response = agent_route(
            user_query=request_body.user_message,
            profile={**request_body.profile, "_request_id": request.state.request_id},
        )

        return enforce_no_advice_language(response)

    except SafetyViolation as sv:
        raise HTTPException(status_code=400, detail=str(sv))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
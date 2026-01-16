from fastapi import FastAPI, HTTPException, Request, Body
from typing import Union, Any, Dict

from src.api.schemas.chat import ChatRequest
from src.api.schemas.request import TaxProfile, TaxProfileV2, convert_v1_to_v2_input
from src.api.schemas.response import TaxRecommendationResponse
from src.api.schemas.scenario_response import ScenarioResponse, ScenarioItemResponse, ScenarioSummary, ScenarioIneligibilityReason

from src.core.recommendation_service import get_tax_recommendation
from src.core.taxfacts import TaxFacts
from src.core.scenario_service import ScenarioService
from src.agent.router import agent_route
from src.agent.normalization_agent import normalize_tax_facts
from src.conversation.memory import ConversationMemory
from src.safety.guardrails import check_domain, enforce_no_advice_language, SafetyViolation
from src.compute.tax_engine import compute_taxable_income_old_regime, compute_old_regime, compute_new_regime

from src.core.logging_config import setup_logging
from src.core.request_logging_middleware import RequestLoggingMiddleware

setup_logging(level="INFO")

app = FastAPI(
    title="WealthWise-AI",
    description="Deterministic tax recommendation API (India)",
    version="2.0.0"
)

app.add_middleware(RequestLoggingMiddleware)

memory = ConversationMemory(max_turns=5)


# =========================================================================
# Helper: Normalize request to TaxFacts (v1 or v2)
# =========================================================================

def normalize_request_to_taxfacts(
    request_body: Union[TaxProfile, TaxProfileV2, dict],
    request_id: str
) -> TaxFacts:
    """
    Convert v1 or v2 request to normalized TaxFacts.
    
    Workflow:
    1. Detect if v1 (TaxProfile) or v2 (TaxProfileV2)
    2. If v1: convert to v2 format using convert_v1_to_v2_input()
    3. If v2: extract tax_facts_input, document_payloads, chat_clarifications
    4. Pass to normalization agent
    5. Return normalized TaxFacts
    
    Args:
        request_body (Union[TaxProfile, TaxProfileV2, dict]): Incoming request
        request_id (str): Request ID for logging
    
    Returns:
        TaxFacts: Normalized, auditable tax facts with provenance
    
    Raises:
        HTTPException: If normalization fails or conflicts unresolved
    """
    
    # If dict, try to detect version and convert to Pydantic object
    if isinstance(request_body, dict):
        version = request_body.get('profile_version', 'v1')
        if version == 'v2':
            try:
                request_body = TaxProfileV2(**request_body)
            except Exception as e:
                raise ValueError(f"Invalid v2 request format: {str(e)}")
        else:
            try:
                request_body = TaxProfile(**request_body)
            except Exception as e:
                raise ValueError(f"Invalid v1 request format: {str(e)}")
    
    # Detect request type
    is_v2 = isinstance(request_body, TaxProfileV2)
    
    if is_v2:
        # V2 request: Extract inputs for normalization
        user_input = request_body.tax_facts_input or {}
        user_identity = request_body.user_identity
        document_payloads = request_body.document_payloads or {}
        chat_data = request_body.chat_clarifications or {}
        
        form16_data = document_payloads.get('form16_data') if isinstance(document_payloads, dict) else getattr(document_payloads, 'form16_data', None)
        extracted_data = document_payloads.get('extracted_data') if isinstance(document_payloads, dict) else getattr(document_payloads, 'extracted_data', None)
    else:
        # V1 request: Convert to v2 format first
        v2_input = convert_v1_to_v2_input(request_body)
        user_input = v2_input
        user_identity = None
        form16_data = None
        extracted_data = None
        chat_data = {}
    
    # Normalize through agent
    try:
        normalization_result = normalize_tax_facts(
            user_input=user_input,
            form16_data=form16_data,
            extracted_data=extracted_data,
            chat_data=chat_data,
            user_identity=user_identity,
        )
    except Exception as e:
        raise ValueError(f"Normalization failed: {str(e)}")
    
    if not normalization_result:
        raise ValueError("Normalization returned None")
    
    # Check for unresolved conflicts
    if hasattr(normalization_result, 'has_unresolved_conflicts') and normalization_result.has_unresolved_conflicts:
        conflicts_str = normalization_result.get_conflicts_summary()
        # Log for debugging; don't fail (user can review in UI)
        # In future: return conflicts in response for user review
        pass
    
    # Add request_id for audit trail
    tax_facts = normalization_result.tax_facts

    # Ensure v2 user inputs are applied (manual inputs should always win)
    if is_v2 and isinstance(user_input, dict):
        for field_name, value in user_input.items():
            if value is None:
                continue
            if hasattr(tax_facts, field_name):
                try:
                    setattr(tax_facts, field_name, value)
                except Exception:
                    # Ignore type coercion issues; normalization already validated
                    pass
    if not hasattr(tax_facts, '_request_id'):
        tax_facts._request_id = request_id
    
    return tax_facts

@app.post(
    "/tax/recommendation",
    response_model=TaxRecommendationResponse,
    tags=["Tax Recommendations"]
)
async def tax_recommendation(request: Request):
    """
    Get tax recommendation (v1 and v2 compatible).
    
    Accepts either:
    - v1 format: TaxProfile (backward compatible)
    - v2 format: TaxProfileV2 (with document extraction, user identity)
    
    Flow:
    1. Parse request body (auto-detect v1 or v2)
    2. Normalize to TaxFacts via normalization agent
    3. Pass to deterministic tax engine
    4. Return recommendation
    
    Request body (v2 example):
    {
        "profile_version": "v2",
        "assessment_year": "2025-26",
        "tax_facts_input": {
            "residential_status": "resident",
            "salary_gross": 1500000,
            "deduction_80c": 150000
        },
        "user_identity": {
            "taxpayer_name": "John Doe",
            "taxpayer_pan": "ABCDE1234F"
        },
        "document_payloads": {
            "form16_data": {...}
        }
    }
    
    Request body (v1 example - still supported):
    {
        "profile_version": "v1",
        "assessment_year": "2025-26",
        "taxpayer": {...},
        "income": {...},
        "deductions_old_regime": {...},
        "taxes_paid": {...},
        "flags": {...}
    }
    """
    import uuid
    import json
    request_id = str(uuid.uuid4())
    
    try:
        # Parse JSON body
        body = await request.json()
        
        # Determine request type based on structure
        if 'tax_facts_input' in body or 'user_identity' in body or 'document_payloads' in body:
            # V2 format detected
            profile = TaxProfileV2(**body)
        else:
            # V1 format (default)
            profile = TaxProfile(**body)
        
        # Normalize to TaxFacts
        try:
            tax_facts = normalize_request_to_taxfacts(profile, request_id)
        except Exception as norm_err:
            raise HTTPException(status_code=400, detail=f"Normalization error: {str(norm_err)}")
        
        # Pass normalized TaxFacts to recommendation engine
        # Convert TaxFacts to dict for compatibility with existing engine
        tax_facts_dict = tax_facts.dict()
        tax_facts_dict['_request_id'] = request_id
        
        try:
            result = get_tax_recommendation(tax_facts_dict)
        except Exception as rec_err:
            raise HTTPException(status_code=400, detail=f"Recommendation error: {str(rec_err)}")
        
        return result
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post(
    "/tax/chat",
    tags=["Chat"]
)
def tax_chat(request_body: ChatRequest, request: Request):
    """
    Chat endpoint (v1 and v2 compatible).
    
    Accepts ChatRequest with either v1 or v2 profile format.
    
    Request format:
    {
        "user_message": "Can I claim 80C deduction?",
        "profile": { ... either v1 or v2 format ... }
    }
    """
    try:
        check_domain(request_body.user_message)
        
        # Normalize user profile to TaxFacts (detects v1 or v2)
        tax_facts = normalize_request_to_taxfacts(
            request_body.profile, 
            request.state.request_id
        )
        
        # Convert to dict for compatibility with agent_route
        tax_facts_dict = tax_facts.dict()
        tax_facts_dict['_request_id'] = request.state.request_id

        response = agent_route(
            user_query=request_body.user_message,
            profile=tax_facts_dict,
        )

        return enforce_no_advice_language(response)

    except SafetyViolation as sv:
        raise HTTPException(status_code=400, detail=str(sv))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =========================================================================
# Scenario Engine Endpoint
# =========================================================================

@app.post(
    "/tax/scenarios",
    response_model=ScenarioResponse,
    tags=["Scenarios"]
)
async def tax_scenarios(request: Request):
    """
    Generate tax optimization scenarios.
    
    Accepts v1 or v2 request formats (auto-detected).
    Computes baseline taxes, then generates applicable scenarios.
    
    Request format (v1):
    {
        "profile_version": "v1",
        "assessment_year": "2024-25",
        "taxpayer": {...},
        "income": {...},
        "deductions": {...},
        ...
    }
    
    Request format (v2):
    {
        "profile_version": "v2",
        "assessment_year": "2024-25",
        "tax_facts_input": {...},
        "user_identity": {...},
        "document_payloads": {...},
        ...
    }
    
    Response: ScenarioResponse with:
    - recommended_regime: Best regime for baseline
    - total_applicable_scenarios: Count of eligible scenarios
    - top_scenarios: Top 3 ranked by tax savings
    - all_applicable_scenarios: All eligible scenarios
    - summary: Stats on all scenarios (including ineligible)
    """
    import uuid
    import json
    request_id = str(uuid.uuid4())
    
    try:
        # Parse JSON body
        body = await request.json()
        
        # Normalize to TaxFacts (auto-detects v1 or v2)
        tax_facts = normalize_request_to_taxfacts(
            request_body=body,
            request_id=request_id
        )
        
        # Compute baseline taxes (old regime)
        # Step 1: Get income breakup
        profile_dict = {
            "income": {
                "salary": tax_facts.salary_gross or 0.0,
                "other_income": 0.0,
                "house_property": {
                    "self_occupied_interest": 0.0,
                    "let_out_net_income": tax_facts.property_letout_net_income or 0.0,
                },
                "capital_gains": {
                    "stcg_111a": tax_facts.capital_gains_stcg_111a or 0.0,
                    "stcg_other": tax_facts.capital_gains_stcg_other or 0.0,
                    "ltcg_112a": tax_facts.capital_gains_ltcg_112a or 0.0,
                    "ltcg_other": tax_facts.capital_gains_ltcg_other or 0.0,
                },
                "business_profession": {
                    "presumptive": {"opted": False},
                    "non_presumptive": {"net_profit": 0.0},
                },
                "deductions": {
                        "section_80c": tax_facts.deduction_80c or 0.0,
                        "80ccd_1b": tax_facts.deduction_80ccd_1b or 0.0,
                          "80d": (tax_facts.deduction_80d_self or 0.0) + 
                              (tax_facts.deduction_80d_spouse or 0.0) + 
                              (tax_facts.deduction_80d_children or 0.0),
                    "80tta": tax_facts.deduction_80tta or 0.0,
                    "80g": tax_facts.deduction_80g or 0.0,
                    "other_chapter_via": 0.0,
                },
            }
        }
        
        income_breakup = compute_taxable_income_old_regime(profile_dict)
        
        # Compute baseline taxes
        baseline_old_tax = compute_old_regime(income_breakup)
        baseline_new_tax = compute_new_regime(income_breakup)
        
        # Generate scenarios using ScenarioService
        scenario_service = ScenarioService(
            baseline_taxfacts=tax_facts,
            baseline_old_tax=baseline_old_tax,
            baseline_new_tax=baseline_new_tax,
        )
        
        # Get response payload (top 3 scenarios + summary)
        payload = scenario_service.to_response_payload(top_n=3)
        
        # Get summary
        summary = scenario_service.get_scenario_summary()
        
        # Build response
        return ScenarioResponse(
            recommended_regime=payload["recommended_regime"],
            total_applicable_scenarios=payload["total_applicable_scenarios"],
            top_scenarios=[ScenarioItemResponse(**s) for s in payload["top_scenarios"]],
            all_applicable_scenarios=[ScenarioItemResponse(**s) for s in payload["all_applicable_scenarios"]],
            summary=ScenarioSummary(
                total_scenarios=summary["total_scenarios"],
                applicable_count=summary["applicable_count"],
                ineligible_count=summary["ineligible_count"],
                ineligible_reasons=[
                    ScenarioIneligibilityReason(**r) 
                    for r in summary["ineligible_reasons"]
                ]
            ),
            note=f"Top 3 scenarios ranked by savings in {payload['recommended_regime']} regime"
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate scenarios: {str(e)}")

# =========================================================================
# Info Endpoints
# =========================================================================

@app.get("/", tags=["Info"])
def root():
    """Root endpoint - API overview."""
    return {
        "name": "WealthWise-AI",
        "version": "2.0.0",
        "description": "Deterministic tax recommendation engine for India",
        "features": [
            "V1 backward compatible (TaxProfile format)",
            "V2 with document extraction (TaxProfileV2 format)",
            "Scenario analysis (tax planning)",
            "Multi-source data normalization (forms, documents, chat)",
            "Full provenance tracking (audit-ready)"
        ],
        "endpoints": {
            "recommendations": "/tax/recommendation (POST)",
            "chat": "/tax/chat (POST)",
            "health": "/health (GET)",
            "schema_v1": "/schema/v1 (GET)",
            "schema_v2": "/schema/v2 (GET)"
        }
    }

@app.get("/health", tags=["Info"])
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "backwards_compatible": True,
        "supported_formats": ["v1 (TaxProfile)", "v2 (TaxProfileV2)"],
        "auto_detection": "Both formats automatically detected"
    }

@app.get("/schema/v1", tags=["Schema"])
def schema_v1():
    """V1 request schema (backward compatible)."""
    return {
        "format": "v1 (TaxProfile)",
        "description": "Original WealthWise format - flat structure with nested objects",
        "example": {
            "profile_version": "v1",
            "assessment_year": 2024,
            "taxpayer": {
                "residential_status": "resident_india",
                "age_category": "below_60"
            },
            "income": {
                "salary_gross": 1200000,
                "capital_gains": 0,
                "other_income": 0
            },
            "deductions_old_regime": {
                "section_80c": 150000,
                "section_80d": 25000,
                "section_80g": 0,
                "home_loan_interest": 200000
            },
            "taxes_paid": {
                "form16_a": 150000,
                "form16_b": 0,
                "advance_tax": 0
            },
            "flags": {
                "has_home_loan": True,
                "has_rental_property": False,
                "has_business_income": False
            }
        },
        "notes": "Still fully supported. POST to /tax/recommendation or /tax/chat"
    }

@app.get("/schema/v2", tags=["Schema"])
def schema_v2():
    """V2 request schema with progressive data entry."""
    return {
        "format": "v2 (TaxProfileV2)",
        "description": "New format enabling document extraction and progressive data entry",
        "progressive_stages": {
            "stage_1_essential": [
                "assessment_year",
                "residential_status",
                "age_category",
                "salary_gross",
                "taxes_paid_tds"
            ],
            "stage_2_conditional": [
                "If has_home_loan: home_loan_interest_paid, home_loan_amount",
                "If has_rental_property: rental_income, property_count",
                "If has_capital_gains: capital_gains_short_term, capital_gains_long_term",
                "If has_dependents: dependents (count)"
            ],
            "stage_3_investments": [
                "deduction_80c_ppf, 80c_lic, 80c_mutual_funds, 80c_other",
                "deduction_80ccd_1b_nps",
                "deduction_80d_self, 80d_spouse, 80d_children, 80d_parents",
                "deduction_80e_education_loan, 80ee_home_loan, 80eea_home_loan, 80gg_rent"
            ],
            "stage_4_documents": [
                "document_payloads.form16_data (Form 16 extraction)",
                "document_payloads.extracted_data (Bank statements, property docs, etc.)"
            ]
        },
        "example": {
            "profile_version": "v2",
            "assessment_year": 2024,
            "tax_facts_input": {
                "residential_status": "resident_india",
                "age_category": "below_60",
                "salary_gross": 1200000,
                "taxes_paid_tds": 150000,
                "home_loan_interest_paid": 200000,
                "deduction_80c_total": 150000,
                "deduction_80ccd_1b_nps": 50000
            },
            "user_identity": {
                "full_name": "John Doe",
                "pan_number": "ABCDE1234F",
                "date_of_birth": "1990-01-15",
                "email": "john@example.com",
                "phone": "+91-9876543210",
                "residential_address": "123 Main St, Bangalore",
                "gender": "male",
                "marital_status": "married"
            },
            "document_payloads": {
                "form16_data": {
                    "employer_name": "Tech Corp",
                    "salary_ctc": 1500000,
                    "tds_deducted": 150000
                },
                "extracted_data": {
                    "bank_statements": "Interest earned: ₹5000",
                    "property_registration": "Property value: ₹50L"
                }
            },
            "chat_clarifications": {
                "has_bonus": True,
                "bonus_amount": 50000,
                "expects_salary_hike": True
            }
        },
        "features": [
            "Supports partial data entry (stage by stage)",
            "Document extraction integration",
            "Multi-source data merging (forms + chats + documents)",
            "Full provenance tracking (source + confidence for each field)",
            "Conflict flagging (user resolves, not auto-override)"
        ],
        "backward_compatibility": "V1 (TaxProfile) auto-converts to V2 format internally"
    }
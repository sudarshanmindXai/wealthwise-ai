# src/api/response.py
from pydantic import BaseModel
from typing import List, Dict, Any


class ITRDecision(BaseModel):
    recommended: str
    reasons: List[str]


class RegimeDecision(BaseModel):
    recommended: str
    old_tax: float
    new_tax: float


class IncomeBreakup(BaseModel):
    gross_total_income: float
    total_deductions_old_regime: float
    taxable_income_old_regime: float


class ExplanationBlock(BaseModel):
    bullets: List[str]
    user_friendly: str


class MissingInfoBlock(BaseModel):
    required: List[str]
    optional: List[str]


class Citation(BaseModel):
    doc_id: str
    file: str
    line_no: int
    text_preview: str


class TaxRecommendationResponse(BaseModel):
    itr: ITRDecision
    regime: RegimeDecision
    income_breakup: IncomeBreakup
    explanation: ExplanationBlock
    missing_info: MissingInfoBlock
    followup_questions: List[str]
    citations: List[Citation]
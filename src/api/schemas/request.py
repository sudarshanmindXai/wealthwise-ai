from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class TaxProfile(BaseModel):
    profile_version: str
    assessment_year: str
    taxpayer: Dict[str, Any]
    income: Dict[str, Any]
    deductions_old_regime: Optional[Dict[str, float]] = {}
    taxes_paid: Optional[Dict[str, float]] = {}
    flags: Dict[str, Any]

    class Config:
        extra = "forbid"
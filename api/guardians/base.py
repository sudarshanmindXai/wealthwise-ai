from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Insight(BaseModel):
    """
    Represents a single optimization insight or finding.
    """
    title: str
    description: str
    impact_currency: float  # Estimated tax saving
    confidence: float # 0.0 to 1.0
    category: str # "deduction", "exemption", "compliance", "warning"
    action_item: Optional[str] = None
    legal_reference: Optional[str] = None # e.g. "Section 80C(2)"
    legal_text: Optional[str] = None # e.g. "Deduction in respect of life insurance premia..."

class UserContext(BaseModel):
    """
    Aggregated user data including profile and ingested documents.
    """
    user_id: str
    regime: str = "new"  # 'old' or 'new'
    income_salary: float = 0.0
    income_interest: float = 0.0
    income_business: float = 0.0
    capital_gains_stcg: float = 0.0
    capital_gains_ltcg: float = 0.0
    investments_80c: float = 0.0
    investments_80d: float = 0.0
    investments_80ccd: float = 0.0
    hra_received: float = 0.0
    rent_paid: float = 0.0
    
    # Advanced fields
    income_rent_received: float = 0.0
    has_crypto_losses: bool = False
    is_ev_owner: bool = False
    turnover_business: float = 0.0 # Gross Receipts
    dividend_income: float = 0.0
    
    documents: List[Dict[str, Any]] = []

class BaseGuardian(ABC):
    """
    Abstract base class for all Tax Guardians.
    """
    
    @property
    @abstractmethod
    def NAME(self) -> str:
        """Name of the guardian"""
        pass

    @abstractmethod
    def analyze(self, context: UserContext) -> List[Insight]:
        """
        Analyze the user context and return a list of optimization insights.
        """
        pass

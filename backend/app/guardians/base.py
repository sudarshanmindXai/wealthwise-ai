"""
WealthWise AI - Guardian Base Classes
=====================================
Common models and base class for all Guardians.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GuardianType(str, Enum):
    """Types of Guardian agents"""
    SALARY_SENTINEL = "salary_sentinel"
    PORTFOLIO_ARCHITECT = "portfolio_architect"
    HUSTLE_SHIELD = "hustle_shield"
    WINDFALL_WARDEN = "windfall_warden"


class Severity(str, Enum):
    """Finding severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Category(str, Enum):
    """Finding categories"""
    OPTIMIZATION = "optimization"
    COMPLIANCE = "compliance"
    RISK = "risk"
    INFORMATION = "information"


@dataclass
class Finding:
    """
    An optimization recommendation or compliance alert from a Guardian.
    """
    guardian: GuardianType
    code: str
    severity: Severity
    category: Category
    title: str
    description: str
    
    # Optional fields
    potential_savings: float = 0.0
    action_required: bool = False
    action_steps: list[str] = field(default_factory=list)
    related_section: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "guardian": self.guardian.value,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "potential_savings": self.potential_savings,
            "action_required": self.action_required,
            "action_steps": self.action_steps,
            "related_section": self.related_section,
        }


@dataclass
class GuardianResult:
    """Result from a Guardian analysis"""
    guardian: GuardianType
    findings: list[Finding]
    taxable_income_contribution: float = 0.0
    metadata: dict = field(default_factory=dict)
    
    @property
    def has_critical(self) -> bool:
        return any(f.severity == Severity.CRITICAL for f in self.findings)
    
    @property
    def total_potential_savings(self) -> float:
        return sum(f.potential_savings for f in self.findings)


class BaseGuardian:
    """Base class for all Guardians"""
    
    guardian_type: GuardianType
    
    def analyze(self, data: dict) -> GuardianResult:
        """Override in subclasses"""
        raise NotImplementedError

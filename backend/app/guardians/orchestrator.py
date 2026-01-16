"""
WealthWise AI - Guardian Orchestrator
======================================
Runs all 4 Guardians in parallel and aggregates results.
"""

from dataclasses import dataclass, field
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from .base import GuardianType, GuardianResult, Finding
from .sentinel_salary import SalarySentinel
from .architect_portfolio import PortfolioArchitect
from .shield_hustle import HustleShield
from .warden_windfall import WindfallWarden


@dataclass
class AuditResult:
    """Complete audit result from all Guardians"""
    results: dict[GuardianType, GuardianResult] = field(default_factory=dict)
    total_taxable_income: float = 0.0
    all_findings: list[Finding] = field(default_factory=list)
    
    @property
    def has_critical_findings(self) -> bool:
        return any(r.has_critical for r in self.results.values())
    
    @property
    def total_potential_savings(self) -> float:
        return sum(r.total_potential_savings for r in self.results.values())
    
    @property
    def finding_count(self) -> dict:
        """Count findings by severity"""
        counts = {"info": 0, "warning": 0, "critical": 0}
        for finding in self.all_findings:
            counts[finding.severity.value] += 1
        return counts
    
    def to_dict(self) -> dict:
        return {
            "total_taxable_income": self.total_taxable_income,
            "total_potential_savings": self.total_potential_savings,
            "has_critical": self.has_critical_findings,
            "finding_counts": self.finding_count,
            "guardians": {
                gt.value: {
                    "taxable_contribution": r.taxable_income_contribution,
                    "findings": [f.to_dict() for f in r.findings],
                    "metadata": r.metadata,
                }
                for gt, r in self.results.items()
            }
        }


class GuardianOrchestrator:
    """
    Orchestrates all 4 Guardians to analyze user's financial profile.
    
    Flow:
    1. Parse income categories from user data
    2. Determine which Guardians to activate
    3. Run active Guardians in parallel
    4. Aggregate results and calculate total tax
    """
    
    def __init__(self):
        self.guardians = {
            GuardianType.SALARY_SENTINEL: SalarySentinel(),
            GuardianType.PORTFOLIO_ARCHITECT: PortfolioArchitect(),
            GuardianType.HUSTLE_SHIELD: HustleShield(),
            GuardianType.WINDFALL_WARDEN: WindfallWarden(),
        }
    
    def analyze(
        self,
        user_data: dict,
        guardians_to_run: Optional[list[GuardianType]] = None,
    ) -> AuditResult:
        """
        Run analysis on user data.
        
        Args:
            user_data: Dictionary containing income/deduction data
            guardians_to_run: Optional list to run specific guardians only
        
        Returns:
            AuditResult with all findings and calculations
        """
        # Determine which guardians to run
        if guardians_to_run is None:
            guardians_to_run = self._detect_active_guardians(user_data)
        
        # Run guardians in parallel
        results: dict[GuardianType, GuardianResult] = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                guardian_type: executor.submit(
                    self.guardians[guardian_type].analyze, user_data
                )
                for guardian_type in guardians_to_run
            }
            
            for guardian_type, future in futures.items():
                try:
                    results[guardian_type] = future.result()
                except Exception as e:
                    print(f"Error in {guardian_type.value}: {e}")
        
        # Aggregate results
        total_taxable = sum(r.taxable_income_contribution for r in results.values())
        all_findings = [f for r in results.values() for f in r.findings]
        
        return AuditResult(
            results=results,
            total_taxable_income=total_taxable,
            all_findings=all_findings,
        )
    
    def _detect_active_guardians(self, data: dict) -> list[GuardianType]:
        """Auto-detect which guardians to activate based on data"""
        active = []
        
        # Check for salary data
        if data.get("salary") or data.get("income", {}).get("salary"):
            active.append(GuardianType.SALARY_SENTINEL)
        
        # Check for investment data
        investments = data.get("investments") or data.get("income", {}).get("investments", {})
        if investments:
            active.append(GuardianType.PORTFOLIO_ARCHITECT)
        
        # Check for freelance data
        if data.get("freelance") or data.get("income", {}).get("freelance"):
            active.append(GuardianType.HUSTLE_SHIELD)
        
        # Check for other income (rental, gifts, HUF)
        if (data.get("rental") or data.get("gifts") or data.get("huf") or
            data.get("interest_income")):
            active.append(GuardianType.WINDFALL_WARDEN)
        
        return active


# Convenience function
def run_audit(user_data: dict) -> AuditResult:
    """Quick function to run full audit"""
    orchestrator = GuardianOrchestrator()
    return orchestrator.analyze(user_data)


# Export
__all__ = ["GuardianOrchestrator", "AuditResult", "run_audit"]

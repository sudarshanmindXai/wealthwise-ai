from .base import BaseGuardian, Insight, UserContext

class SalarySentinel(BaseGuardian):
    NAME = "Salary Sentinel"

    def analyze(self, context: UserContext) -> list[Insight]:
        insights = []

        # 1. HRA Analysis
        # If user receives HRA but pays rent and hasn't claimed it fully (simplified logic)
        if context.hra_received > 0 and context.rent_paid > 0:
            # In a real scenario, we'd calculate exact exemption.
            # Here we just flag if it looks like they could save.
            
            # Simple heuristic: If rent paid is substantial but they are in New Regime (default),
            # suggest checking Old Regime or ensuring HRA is claimed if staying in Old.
            
            # For now, let's assume if rent > 1L/yr and regime is 'new', it's a potential switch trigger
            if context.regime == "new" and context.rent_paid > 100000:
                insights.append(Insight(
                    title="Significant Rent Paid",
                    description=f"You are paying ₹{context.rent_paid:,} in rent. The Old Regime with HRA exemption might be more beneficial than the New Regime.",
                    impact_currency=context.hra_received * 0.30, # Approx 30% tax bracket saving
                    confidence=0.85,
                    category="deduction",
                    action_item="Check 'Regime Comparison' to see if switching saves tax."
                ))

        # 2. NPS 80CCD(2) Arbitrage
        # If salary is high (>10L) and no 80CCD contribution detected
        if context.income_salary > 1000000 and context.investments_80ccd == 0:
             # Employer NPS contribution is exempt up to 10% of Basic+DA even in New Regime
             # Estimating Basic as 40% of Salary
             estimated_basic = context.income_salary * 0.40
             max_contribution = estimated_basic * 0.10
             
             insights.append(Insight(
                 title="Missed NPS Tax Shield",
                 description="You are missing out on Section 80CCD(2). Employer contributions to NPS are tax-exempt even in the New Regime.",
                 impact_currency=max_contribution * 0.30, # Tax saved
                 confidence=0.95,
                 category="exemption",
                 action_item="Ask your employer to restructure your salary to include NPS contribution (up to 10% of Basic)."
             ))

        return insights

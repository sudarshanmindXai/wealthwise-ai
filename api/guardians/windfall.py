from .base import BaseGuardian, Insight, UserContext

class WindfallWarden(BaseGuardian):
    NAME = "Windfall Warden"

    def analyze(self, context: UserContext) -> list[Insight]:
        insights = []

        # Logic for Rent Received / Other Sources
        # We don't have a direct 'rent_received' field in UserContext yet, 
        # but let's assume it might be part of 'documents' or we add it to context later.
        # For MVP, checking 'income_house_property' if we had it, or inferring.
        
        # Placeholder logic: scan documents for rent receipts? 
        # Or simple check on Other Income if substantial.
        
        # 1. Rental Income Standard Deduction (Section 24)
        if context.income_rent_received > 0:
            std_deduction = context.income_rent_received * 0.30
            insights.append(Insight(
                title="Rental Income Standard Deduction",
                description=f"You are eligible for a flat 30% deduction (₹{std_deduction:,}) on your gross rental receipts of ₹{context.income_rent_received:,}, regardless of actual expenses.",
                impact_currency=std_deduction * 0.30, # Tax saved at 30% slab
                confidence=1.0,
                category="deduction",
                action_item="Ensure this 30% deduction is applied in your ITR House Property schedule.",
                legal_reference="Section 24(a)"
            ))

        # 2. Gift Taxation (Basic Heuristic)
        # If 'gifts' are found in documents (not yet in context but logic ready)
        # Assuming we might add 'income_other_gifts' later. For now, skipping.
        pass

        return insights

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
        
        pass # To be fleshed out as we have better data inputs.

        return insights

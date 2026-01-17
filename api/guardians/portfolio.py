from .base import BaseGuardian, Insight, UserContext

class PortfolioArchitect(BaseGuardian):
    NAME = "Portfolio Architect"

    def analyze(self, context: UserContext) -> list[Insight]:
        insights = []

        # 1. 1.25L LTCG Exemption (Sec 112A)
        # Check if they have utilized the limit
        ltcg_limit = 125000
        if context.capital_gains_ltcg > 0:
            if context.capital_gains_ltcg < ltcg_limit:
                 remaining = ltcg_limit - context.capital_gains_ltcg
                 insights.append(Insight(
                    title="Unused LTCG Limit",
                    description=f"You have realized ₹{context.capital_gains_ltcg:,} in Long Term Capital Gains. You have ₹{remaining:,} of tax-free gains remaining for this year.",
                    impact_currency=remaining * 0.125, # 12.5% tax saved on future gains
                    confidence=0.90,
                    category="exemption",
                    action_item=f"Consider harvesting ₹{remaining:,} more in LTCG to reset cost basis tax-free."
                ))
            else:
                 # Exceeded limit
                 taxable_excess = context.capital_gains_ltcg - ltcg_limit
                 insights.append(Insight(
                    title="LTCG Limit Exceeded",
                    description=f"You have exceeded the ₹1.25 Lakh tax-free limit by ₹{taxable_excess:,}. This excess is taxed at 12.5%.",
                    impact_currency=-(taxable_excess * 0.125), # Tax cost
                    confidence=1.0,
                    category="info",
                    action_item="Plan for 12.5% tax outflow on these gains."
                ))
        elif context.capital_gains_ltcg == 0:
            # Totally unused
             insights.append(Insight(
                title="LTCG Harvesting Opportunity",
                description="You haven't realized any Long Term Capital Gains this year. The first ₹1.25 Lakhs is tax-free.",
                impact_currency=ltcg_limit * 0.125,
                confidence=0.80,
                category="exemption",
                action_item="Review your portfolio for stocks/MFs held >1 year with gains. Sell and rebuy to 'harvest' tax-free gains."
            ))

        # 2. Crypto Analysis (Section 115BBH)
        if context.has_crypto_losses:
             insights.append(Insight(
                title="Crypto Loss Trap (Sec 115BBH)",
                description="Losses from Virtual Digital Assets (Crypto/NFTs) CANNOT be set off against any other income, including Crypto gains from another token.",
                impact_currency=0, # It's a dead loss
                confidence=1.0,
                category="warning",
                action_item="Do not bank on offsetting these losses to reduce your tax liability.",
                legal_reference="Section 115BBH(2)(b)"
            ))

        # 3. Dividend & Buyback Impact (Budget 2024 update)
        # Buybacks are now taxed as Deemed Dividend
        if context.dividend_income > 5000:
            insights.append(Insight(
                title="Dividend Tax Alert",
                description=f"Your dividend income of ₹{context.dividend_income:,} is fully taxable at your slice rate. TDS at 10% applies if >₹5,000.",
                impact_currency=-(context.dividend_income * 0.30), # Assuming 30% slab
                confidence=1.0,
                category="info",
                action_item="Ensure you have paid Advance Tax on this dividend income to avoid 234C interest.",
                legal_reference="Section 194"
            ))
        
        return insights

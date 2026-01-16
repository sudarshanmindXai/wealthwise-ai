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

        # 2. Crypto Analysis (Placeholder - assumes documents might contain crypto info in future)
        # For now, we don't have direct crypto input in context, but adding logic as if we extracted it
        # If we had a flag check:
        # if context.has_crypto_losses:
        #    insights.append(...)
        
        return insights

from .base import BaseGuardian, Insight, UserContext

class HustleShield(BaseGuardian):
    NAME = "Hustle Shield"

    def analyze(self, context: UserContext) -> list[Insight]:
        insights = []

        # 1. Section 44ADA Optimization for Professionals
        # If there is business/freelance income
        if context.income_business > 1000:
            # Presumptive checks
            limit_44ada = 7500000 # 75 Lakhs
            
            if context.income_business <= limit_44ada:
                # Calculate tax saved vs declaring 100% vs 50%
                # In normal biz, you declare Expenses. 
                # Presumptive assumes 50% flat.
                
                presumptive_profit = context.income_business * 0.50
                # Assuming 30% tax bracket for impact calc
                tax_savings_potential = presumptive_profit * 0.30
                
                insights.append(Insight(
                    title="Presumptive Taxation (Sec 44ADA)",
                    description=f"For your freelance income of ₹{context.income_business:,}, you can declare just 50% as profit under Section 44ADA, provided you are a specified professional.",
                    impact_currency=tax_savings_potential,
                    confidence=0.95,
                    category="deduction",
                    action_item="Ensure you file under Section 44ADA to slash taxable business income by half without maintaining detailed expense books.",
                    legal_reference="Section 44ADA"
                ))
            else:
                 insights.append(Insight(
                    title="Audit Risk Warning",
                    description=f"Your business income of ₹{context.income_business:,} exceeds the ₹75 Lakh limit for Section 44ADA. You must maintain books of accounts and get an audit.",
                    impact_currency=0,
                    confidence=1.0,
                    category="compliance",
                    action_item="Consult a CA immediately for Audit requirements.",
                    legal_reference="Section 44AB"
                ))
        
        # 2. GST Monitoring
        # If turnover > 20L (Services) or 40L (Goods), GST is mandatory
        # We use income_business as proxy for turnover for services
        gst_threshold = 2000000
        if context.turnover_business > gst_threshold or context.income_business > gst_threshold:
             insights.append(Insight(
                title="Mandatory GST Registration",
                description="Your gross receipts exceed ₹20 Lakhs. You are mandated to register for GST and charge 18% on your invoices.",
                impact_currency=0, # Compliance cost primarily
                confidence=1.0,
                category="compliance",
                action_item="Register for GST immediately to avoid penalties.",
                legal_reference="GST Act"
            ))

        return insights

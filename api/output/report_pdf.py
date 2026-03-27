from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, Any, List
from io import BytesIO
from datetime import datetime

class ReportPDFGenerator:
    def __init__(self, data: Dict[str, Any]):
        """
        data expected schema:
        {
            "user": { ... },
            "analysis": {
                "gross_income": float,
                "taxable_income": float,
                "tax_old": float,
                "tax_new": float,
                "regime": "new" | "old",
                "savings": float
            },
            "insights": [
                {"title": str, "description": str, "category": str, "impact_currency": float}
            ]
        }
        """
        self.data = data
        self.styles = getSampleStyleSheet()
        self.doc = None
        self.elements = []
    
    def generate(self) -> bytes:
        buffer = BytesIO()
        self.doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        
        self._add_title_page()
        self._add_executive_summary()
        self._add_tax_breakdown()
        self._add_insights()
        self._add_disclaimer()
        
        self.doc.build(self.elements)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_title_page(self):
        # Title
        style_title = ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor("#059669") # Emerald 600
        )
        self.elements.append(Paragraph("WealthWise AI", style_title))
        
        self.elements.append(Paragraph("Detailed Tax Analysis Report", self.styles['Heading2']))
        self.elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y')}", self.styles['Normal']))
        self.elements.append(Spacer(1, 40))
        
        # User Info
        u = self.data.get('user', {})
        user_info = [
            ["Taxpayer Name", u.get('name', 'Client')],
            ["Financial Year", "2025-26"],
            ["PAN", u.get('pan', 'Not Provided')]
        ]
        t = Table(user_info, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 20))

    def _add_executive_summary(self):
        self.elements.append(Paragraph("Executive Summary", self.styles['Heading2']))
        
        an = self.data.get('analysis', {})
        regime = "New Tax Regime" if an.get('regime') == "new" else "Old Tax Regime"
        savings = an.get('savings', 0)
        
        summary_text = f"Based on your financial data, we recommend opting for the <b>{regime}</b>. This choice is projected to save you approximately <b>Rs. {savings:,.0f}</b> compared to the alternative."
        self.elements.append(Paragraph(summary_text, self.styles['Normal']))
        self.elements.append(Spacer(1, 12))
        
        # Summary Table
        data = [
            ["Metric", "Value (Rs.)"],
            ["Gross Total Income", f"{an.get('gross_income', 0):,.2f}"],
            ["Taxable Income", f"{an.get('taxable_income', 0):,.2f}"],
            ["Net Tax Payable", f"{an.get('tax_payable', 0):,.2f}"]
        ]
        
        self._create_simple_table(data)

    def _add_tax_breakdown(self):
        self.elements.append(Paragraph("Tax Calculation Breakdown", self.styles['Heading2']))
        
        an = self.data.get('analysis', {})
        
        data = [
            ["Regime Comparison", "Old Regime", "New Regime"],
            ["Tax Payable", f"{an.get('tax_old', 0):,.2f}", f"{an.get('tax_new', 0):,.2f}"],
            ["Difference", "", f"{abs(an.get('tax_old', 0) - an.get('tax_new', 0)):,.2f}"]
        ]
        
        t = Table(data, colWidths=[200, 150, 150])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 12))

    def _add_insights(self):
        insights = self.data.get('insights', [])
        if not insights:
            return
            
        self.elements.append(Paragraph("AI Guardian Insights", self.styles['Heading2']))
        
        for item in insights:
            cat = item.get('category', 'info').upper()
            color = colors.red if cat == 'WARNING' else colors.blue
            
            # Title
            self.elements.append(Paragraph(f"<b>[{cat}] {item.get('title')}</b>", ParagraphStyle('InTitle', parent=self.styles['Normal'], textColor=color)))
            
            # Desc
            self.elements.append(Paragraph(item.get('description', ''), self.styles['Normal']))
            
            # Impact
            impact = item.get('impact_currency', 0)
            if impact > 0:
                 self.elements.append(Paragraph(f"<b>Potential Saving: Rs. {impact:,.2f}</b>", ParagraphStyle('Impact', parent=self.styles['Normal'], textColor=colors.green)))
            
            self.elements.append(Spacer(1, 10))

    def _add_disclaimer(self):
        self.elements.append(Spacer(1, 40))
        disclaimer = "<b>Disclaimer:</b> This report is generated by an AI system (WealthWise AI) for informational purposes only. It does not constitute legal or certified financial advice. Please consult a Chartered Accountant before filing your taxes."
        self.elements.append(Paragraph(disclaimer, ParagraphStyle('Disclaimer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey)))

    def _create_simple_table(self, data):
        t = Table(data, colWidths=[250, 150])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 12))

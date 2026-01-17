from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, Any, List
from io import BytesIO

class Form12BBGenerator:
    def __init__(self, data: Dict[str, Any]):
        """
        data expected schema:
        {
            "user": {
                "name": str,
                "address": str,
                "pan": str,
                "father_name": str,
                "designation": str,
                "financial_year": str
            },
            "hra": {
                "rent_paid": float,
                "landlord_name": str,
                "landlord_pan": str,
                "address": str
            },
            "lta": float,
            "home_loan_interest": {
                "amount": float,
                "lender_name": str,
                "lender_pan": str
            },
            "deductions_80c": [
                {"description": "Life Insurance", "amount": 50000},
                {"description": "PPF", "amount": 100000}
            ],
            "deductions_points": { # Other chapter VI-A
                "80D": float,
                "80E": float,
                "80G": float,
                "80TTA": float
            }
        }
        """
        self.data = data
        self.styles = getSampleStyleSheet()
        self.doc = None
        self.elements = []
    
    def generate(self) -> bytes:
        buffer = BytesIO()
        self.doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        
        self._add_header()
        self._add_personal_info()
        self._add_hra_section()
        self._add_lta_section()
        self._add_home_loan_section()
        self._add_chapter_via_section()
        self._add_verification()
        
        self.doc.build(self.elements)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_header(self):
        style = ParagraphStyle(
            name='Header',
            parent=self.styles['Heading1'],
            alignment=1, # Center
            fontSize=14,
            spaceAfter=6
        )
        self.elements.append(Paragraph("<b>FORM NO. 12BB</b>", style))
        
        sub_style = ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Normal'],
            alignment=1,
            fontSize=10
        )
        self.elements.append(Paragraph("(See rule 26C)", sub_style))
        self.elements.append(Paragraph(f"Statement for claims by employee for deduction of tax", sub_style))
        self.elements.append(Spacer(1, 12))

    def _add_personal_info(self):
        u = self.data.get('user', {})
        
        data = [
            ["1. Name and address of the employee", f"{u.get('name', '')}\n{u.get('address', '')}"],
            ["2. Permanent Account Number (PAN) of the employee", u.get('pan', '')],
            ["3. Financial Year", u.get('financial_year', '2025-26')]
        ]
        
        t = Table(data, colWidths=[200, 300])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 12))

    def _add_hra_section(self):
        self.elements.append(Paragraph("<b>House Rent Allowance</b>", self.styles['Heading4']))
        hra = self.data.get('hra', {})
        
        data = [
            ["Nature of Claim", "Details", "Amount (Rs.)"],
            ["Rent paid to the landlord", f"Name: {hra.get('landlord_name', 'NA')}\nAddress: {hra.get('address', 'NA')}\nPAN: {hra.get('landlord_pan', 'NA')}", f"{hra.get('rent_paid', 0):,.2f}"]
        ]
        
        self._create_section_table(data)

    def _add_lta_section(self):
        self.elements.append(Paragraph("<b>Leave Travel Concessions or Assistance</b>", self.styles['Heading4']))
        amount = self.data.get('lta', 0)
        data = [
            ["Nature of Claim", "Amount (Rs.)"],
            ["Leave Travel Concession/Assistance", f"{amount:,.2f}"]
        ]
        self._create_section_table(data, col_widths=[350, 150])

    def _add_home_loan_section(self):
        self.elements.append(Paragraph("<b>Deduction of Interest on Borrowing (House Property)</b>", self.styles['Heading4']))
        hl = self.data.get('home_loan_interest', {})
        
        data = [
            ["Interest payable/paid to the lender", f"Name: {hl.get('lender_name', 'NA')}\nPAN: {hl.get('lender_pan', 'NA')}", f"{hl.get('amount', 0):,.2f}"]
        ]
        self._create_section_table(data)

    def _add_chapter_via_section(self):
        self.elements.append(Paragraph("<b>Deduction under Chapter VI-A</b>", self.styles['Heading4']))
        
        # Section 80C
        rows = [["<b>(A) Section 80C, 80CCC and 80CCD</b>", "", ""]]
        ded_80c = self.data.get('deductions_80c', [])
        total_80c = 0
        
        if not ded_80c:
            rows.append(["No investments declared under 80C", "", "0.00"])
        else:
            for d in ded_80c:
                rows.append([d.get('description', 'Investment'), "", f"{d.get('amount', 0):,.2f}"])
                total_80c += d.get('amount', 0)
        
        rows.append(["Total Section 80C", "", f"<b>{total_80c:,.2f}</b>"])
        
        # Other Sections
        rows.append(["<b>(B) Other Sections (e.g. 80D, 80E, 80G)</b>", "", ""])
        others = self.data.get('deductions_points', {})
        total_other = 0
        
        for section, amt in others.items():
            rows.append([f"Section {section}", "", f"{amt:,.2f}"])
            total_other += amt
            
        rows.append(["Total Chapter VI-A Deductions", "", f"<b>{total_80c + total_other:,.2f}</b>"])
        
        self._create_section_table(rows, header=["Section", "Details", "Amount (Rs.)"])

    def _add_verification(self):
        self.elements.append(Spacer(1, 24))
        u = self.data.get('user', {})
        
        verify_text = f"""
        <b>Verification</b><br/><br/>
        I, <b>{u.get('name', '___')}</b>, son/daughter of <b>{u.get('father_name', '___')}</b>, do hereby certify that the information given above is complete and correct.<br/><br/>
        Place: __________________ <br/><br/>
        Date: ___________________ <br/><br/>
        
        (Signature of the Employee)<br/>
        Designation: {u.get('designation', '___')}
        """
        
        self.elements.append(Paragraph(verify_text, self.styles['Normal']))

    def _create_section_table(self, data, header=None, col_widths=None):
        if not col_widths:
            col_widths = [150, 200, 150]
        
        # If header provided but not in data[0], prepend it (logic can vary, here assuming data has header if header arg is None)
        if header and data[0] != header:
             # This check is weak, but for now assuming caller handles data structure or I force common structure.
             pass 

        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Header row bold
            ('ALIGN', (-1,0), (-1,-1), 'RIGHT'), # Amount column right align
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 12))

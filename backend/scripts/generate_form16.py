from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_form16(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, fontSize=14)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], alignment=1, fontSize=11)
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
    
    # --- Header ---
    elements.append(Paragraph("FORM NO. 16", title_style))
    elements.append(Paragraph("[See rule 31(1)(a)]", subtitle_style))
    elements.append(Paragraph("PART B", title_style))
    elements.append(Paragraph("Certificate under section 203 of the Income-tax Act, 1961", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Personal Details ---
    # In a real form, this is often side-by-side or a table. We'll use a table.
    details_data = [
        ["Last updated on", "16-Jan-2026"],
        ["Assessment Year", "2026-27"], # FY 2025-26
        ["Name and address of the Employer", "Name and address of the Employee"],
        ["TechNova Solutions Pvt Ltd\nTech Park, Sector 45\nGurgaon, Haryana - 122003\nPAN: TNSP12345L\nTAN: DELT12345A", 
         "Vikram Rathore\nFlat 402, Oakwood Residency\nIndiranagar, Bangalore - 560038\nPAN: ABCDE1234F"]
    ]
    
    t_details = Table(details_data, colWidths=[3.5*inch, 3.5*inch])
    t_details.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
        ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
    ]))
    elements.append(t_details)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Details of Salary paid and any other income and tax deducted", bold_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # --- Salary Details Table ---
    # Structure: S.No | Particulars | Amount 1 | Amount 2 | Amount 3
    
    salary_data = [
        ["1.", "Gross Salary", "", "", "45,00,000"],
        ["(a)", "Salary as per provisions contained in sec 17(1)", "42,00,000", "", ""],
        ["(b)", "Value of perquisites u/s 17(2)", "3,00,000", "", ""],
        ["(c)", "Profits in lieu of salary u/s 17(3)", "0", "", ""],
        ["(d)", "Total", "", "45,00,000", ""],
        
        ["2.", "Less: Allowances to the extent exempt u/s 10", "", "", ""],
        ["(a)", "Travel concession or assistance u/s 10(5)", "50,000", "", ""],
        ["(b)", "House Rent Allowance u/s 10(13A)", "3,00,000", "", ""],
        ["(c)", "Total", "", "3,50,000", ""],
        
        ["3.", "Balance (1 - 2)", "", "", "41,50,000"],
        
        ["4.", "Deductions under section 16:", "", "", ""],
        ["(a)", "Standard Deduction u/s 16(ia)", "", "50,000", ""],
        ["(b)", "Entertainment allowance u/s 16(ii)", "", "0", ""],
        ["(c)", "Tax on employment u/s 16(iii)", "", "2,400", ""],
        
        ["5.", "Aggregate of 4(a), 4(b) and 4(c)", "", "", "52,400"],
        
        ["6.", "Income chargeable under the head 'Salaries' (3-5)", "", "", "40,97,600"],
        
        ["7.", "Add: Any other income reported by the employee", "", "", ""],
        ["(a)", "Income from House Property", "", "-2,00,000", ""], # Loss from self-occupied
        ["(b)", "Income from Other Sources", "", "50,000", ""],
        
        ["8.", "Gross Total Income (6 + 7)", "", "", "39,47,600"],
        
        ["9.", "Deductions under Chapter VI-A", "", "", ""],
        ["(a)", "80C (LIC, PF, PPF, etc.)", "1,50,000", "", ""],
        ["(b)", "80D (Health Insurance)", "25,000", "", ""],
        ["(c)", "80CCD(1B) (NPS)", "50,000", "", ""],
        ["(d)", "Total Deductions", "", "", "2,25,000"],
        
        ["10.", "Total Income (8 - 9)", "", "", "37,22,600"],
        
        ["11.", "Tax on Total Income", "", "", "9,41,780"],
        
        ["12.", "Surcharge (if applicable)", "", "", "0"],
        
        ["13.", "Health and Education Cess @ 4%", "", "", "37,671"],
        
        ["14.", "Tax Payable (11+12+13)", "", "", "9,79,451"],
        
        ["15.", "Less: Relief under section 89", "", "", "0"],
        
        ["16.", "Net Tax Payable", "", "", "9,79,451"],
        
        ["17.", "Taxes Deducted", "", "", "9,79,451"],
         ["18.", "Tax Payable/Refundable", "", "", "0"],
    ]
    
    t_salary = Table(salary_data, colWidths=[0.5*inch, 3.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    t_salary.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        
        # Bold rows for totals
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Row 1
        ('FONTNAME', (0,9), (-1,9), 'Helvetica-Bold'), # Row 3 (Balance)
        ('FONTNAME', (0,15), (-1,15), 'Helvetica-Bold'), # Row 6 (Income Salaries)
        ('FONTNAME', (0,19), (-1,19), 'Helvetica-Bold'), # Row 8 (GTI)
        ('FONTNAME', (0,25), (-1,25), 'Helvetica-Bold'), # Row 10 (Total Income)
        ('FONTNAME', (0,29), (-1,29), 'Helvetica-Bold'), # Tax Payable
    ]))
    
    elements.append(t_salary)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Verification ---
    verification_text = """
    I, <b>Mahesh Kumar</b>, son/daughter of <b>Suresh Kumar</b>, working in the capacity of <b>Finance Manager</b> 
    (designation) do hereby certify that the information given above is true, complete and correct and is based on the 
    books of account, documents, TDS statements, and other available records.
    """
    elements.append(Paragraph("Verification", bold_style))
    elements.append(Paragraph(verification_text, normal_style))
    elements.append(Spacer(1, 0.5*inch))
    
    elements.append(Paragraph("Place: Gurgaon", normal_style))
    elements.append(Paragraph("Date: 16-Jan-2026", normal_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("(Signature of person responsible for deduction of tax)", normal_style))
    elements.append(Paragraph("Full Name: Mahesh Kumar", normal_style))

    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_form16("wealthwise/backend/sample_docs/form16_vikram.pdf")

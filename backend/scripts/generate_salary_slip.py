from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pathlib import Path

def generate_salary_slip(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, fontSize=16)
    company_style = ParagraphStyle('Company', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=2)
    address_style = ParagraphStyle('Address', parent=styles['Normal'], alignment=1, fontSize=10)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], alignment=1, fontSize=12, fontName='Helvetica-Bold')
    
    # --- Company Header ---
    elements.append(Paragraph("TechNova Solutions Private Limited", company_style))
    elements.append(Paragraph("#45, Tech Park, Sector 45, Gurgaon, Haryana - 122003", address_style))
    elements.append(Paragraph("CIN: U72200KA2010PTC123456", address_style))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Pay Slip for April-2025", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Employee Details ---
    # 2-column layout using Table
    emp_data = [
        ["Name", "Vikram Rathore", "Employee No", "TNS-1098"],
        ["Designation", "VP Engineering", "PAN", "ABCDE1234F"],
        ["Department", "Product & Engg", "Bank Name", "HDFC Bank"],
        ["Location", "Bangalore", "Bank A/c No", "50100123456789"],
        ["Date of Joining", "01-Apr-2018", "UAN", "100900800700"],
        ["Days Worked", "30", "PF No", "GN/GGN/0012345/000/123"],
    ]
    
    t_info = Table(emp_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 2.0*inch])
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), # Label col 1
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'), # Label col 3
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Earnings & Deductions Table ---
    # Structure: Earnings | Amount | Deductions | Amount
    
    earnings_header = ["Earnings", "Amount (Rs.)", "Deductions", "Amount (Rs.)"]
    
    # Figures based on ~45L CTC/year => ~3.75L/month gross
    earnings_data = [
        ["Basic Salary", "1,50,000.00", "Provident Fund", "12,000.00"],
        ["House Rent Allowance", "75,000.00", "Professional Tax", "200.00"],
        ["Special Allowance", "1,25,000.00", "Income Tax (TDS)", "85,000.00"],
        ["Conveyance Allowance", "10,000.00", "", ""],
        ["Medical Allowance", "15,000.00", "", ""],
        ["", "", "", ""],
        ["Total Earnings", "3,75,000.00", "Total Deductions", "97,200.00"],
    ]
    
    # Net Pay
    net_pay_val = "2,77,800.00"
    
    # Table Data
    table_data = [earnings_header] + earnings_data
    
    t_salary = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 2.0*inch, 1.2*inch])
    t_salary.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), # Header
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'), # Amounts Right Align
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        
        # Total Row Bold
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.whitesmoke),
    ]))
    elements.append(t_salary)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Net Pay Box ---
    net_text = f"Net Pay: Rs. {net_pay_val}"
    net_words = f"(Rupees Two Lakh Seventy Seven Thousand Eight Hundred Only)"
    
    elements.append(Paragraph(net_text, header_style))
    elements.append(Paragraph(net_words, styles['Italic']))
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("** This is a computer generated document and does not require signature **", 
                              ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, fontSize=8)))

    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == "__main__":
    output_dir = Path("wealthwise/backend/sample_docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_salary_slip(str(output_dir / "salary_slip_vikram.pdf"))

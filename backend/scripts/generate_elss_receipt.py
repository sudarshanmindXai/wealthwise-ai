from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pathlib import Path
import random
from datetime import datetime

def generate_elss_receipt(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, fontSize=14)
    normal_style = styles['Normal']
    
    # --- Header ---
    elements.append(Paragraph("PAYMENT CONFIRMATION", title_style))
    elements.append(Paragraph("Dear Vikram Rathore, Date: 15/01/2026", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("Thank you for investing through ETMONEY.", normal_style))
    elements.append(Paragraph("Please find below the payment receipt containing details of your online transaction.", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Investor Details ---
    elements.append(Paragraph("<b>Investor Details:</b>", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    inv_data = [
        ["Investor Name", "Vikram Rathore"],
        ["PAN", "ABCDE1234F"]
    ]
    t_inv = Table(inv_data, colWidths=[2*inch, 3*inch], hAlign='LEFT')
    t_inv.setStyle(TableStyle([
         ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t_inv)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Transaction Details ---
    elements.append(Paragraph("<b>Transaction Details:</b>", normal_style))
    
    headers = ["Transaction\nNumber", "Fund Name", "Scheme Name", "Scheme\nCategory", "Amount", "Transaction\nDate"]
    
    # Generate 3 transactions to total ~1.5L
    txns = [
        ["TXN123456789", "Aditya Birla Sun Life", "Tax Relief 96 Direct", "ELSS", "50,000", "05/04/2025"],
        ["TXN987654321", "Axis Mutual Fund", "Long Term Equity Direct", "ELSS", "50,000", "15/06/2025"],
        ["TXN456123789", "DSP Mutual Fund", "Tax Saver Direct Plan", "ELSS", "50,000", "10/12/2025"],
    ]
    
    data = [headers] + txns
    
    t_txns = Table(data, colWidths=[1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch, 1.0*inch, 1.0*inch])
    t_txns.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (4,1), (4,-1), 'RIGHT'), # Amounts
    ]))
    elements.append(t_txns)
    elements.append(Spacer(1, 0.5*inch))
    
    # --- Footer ---
    elements.append(Paragraph("Note: This receipt shall be considered null and void in case of Cancellation of the Investment by the mutual fund company.", normal_style))
    elements.append(Paragraph("In case of any further clarification or assistance kindly write back to us at help@etmoney.com", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Regards,", normal_style))
    elements.append(Paragraph("TEAM ETMONEY", ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')))

    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == "__main__":
    output_dir = Path("wealthwise/backend/sample_docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_elss_receipt(str(output_dir / "elss_receipt_vikram.pdf"))

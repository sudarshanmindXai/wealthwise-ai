from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Salary Slip for October 2025", ln=1, align="C")
pdf.cell(200, 10, txt="Company: Tech Corp", ln=1, align="C")
pdf.cell(200, 10, txt="Employee: Siddhant", ln=1)
pdf.cell(200, 10, txt="PAN: ABCDE1234F", ln=1)
pdf.cell(200, 10, txt="Bank A/c No: 1234567890", ln=1)
pdf.cell(200, 10, txt="", ln=1)
pdf.cell(200, 10, txt="Earnings:", ln=1)
pdf.cell(200, 10, txt="Basic Salary: 100000", ln=1)
pdf.cell(200, 10, txt="HRA: 50000", ln=1)
pdf.cell(200, 10, txt="", ln=1)
pdf.cell(200, 10, txt="Deductions:", ln=1)
pdf.cell(200, 10, txt="PF Deduction: 12000", ln=1)
pdf.cell(200, 10, txt="Income Tax (TDS): 5000", ln=1)
pdf.cell(200, 10, txt="", ln=1)
# Intentionally using "Net Salary" to test if the parser handles it, 
# or if it fails because it strictly wants "Net Pay"
pdf.cell(200, 10, txt="Net Salary: 133000.00", ln=1)

pdf.output("test_salary.pdf")
print("Created test_salary.pdf")

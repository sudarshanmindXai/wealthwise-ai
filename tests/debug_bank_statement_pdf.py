
import requests
import time
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Create dummy PDF
def create_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    data = [
        ["Date", "Description", "Ref No", "Debit", "Credit", "Balance"],
        ["01-04-2024", "UPI-SWIGGY", "REF123", "500.00", "", "50000.00"],
        ["02-04-2024", "SALARY", "REF124", "", "100000.00", "150000.00"],
        ["03-04-2024", "NETFLIX", "REF125", "649.00", "", "149351.00"],
        ["04-04-2024", "DUMMY", "REF126", "", "", "149351.00"] # Empty row
    ]
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    doc.build(elements)

pdf_path = "tests/dummy_statement.pdf"
create_pdf(pdf_path)

url = "http://localhost:8000/api/v1/ingest/upload"
files = {"file": open(pdf_path, "rb")}

print(f"Uploading PDF to {url}...")
try:
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        task_id = data["task_id"]
        print(f"Task ID: {task_id}")
        
        # Poll
        for _ in range(15):
            time.sleep(1)
            status_url = f"http://localhost:8000/api/v1/ingest/status/{task_id}"
            status_res = requests.get(status_url)
            status_data = status_res.json()
            print(f"Poll Status: {status_data.get('status')} | Progress: {status_data.get('progress')}")
            
            if status_data.get("status") == "complete":
                result = status_data.get("result", {})
                txns = result.get("raw_data", {}).get("transactions", [])
                print(f"\n✅ Success! Found {len(txns)} transactions.")
                for t in txns:
                    print(f" - {t['date']} | {t['description']} | {t['type']} | {t['amount']}")
                break
            
            elif status_data.get("status") in ["error", "failed"]:
                 print(f"❌ Error: {status_data.get('error')}")
                 break
                 
    else:
        print(f"❌ Upload Failed: {response.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")

finally:
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

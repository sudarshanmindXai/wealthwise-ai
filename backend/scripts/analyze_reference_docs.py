import pandas as pd
import pdfplumber
import re
from pathlib import Path

# Paths to reference documents
DOCS = {
    "Bank Statement (XLS)": "wealthwise/backend/sample_docs/sidd_bank stement.xls",
    "Salary Slip (PDF)": "wealthwise/backend/sample_docs/siddhant_salary_slip.pdf",
    "Form 16 (PDF)": "wealthwise/backend/sample_docs/form_16_sidd.pdf",
    "ELSS Receipt (PDF)": "wealthwise/backend/sample_docs/_ELSS_Payment_Receipt.pdf",
    "Zerodha P&L (XLSX)": "wealthwise/backend/sample_docs/Zerodha_pnl.xlsx"
}

def mask_pii(text):
    """Simple masker for digits and potential names/emails"""
    if not isinstance(text, str):
        text = str(text)
    
    # Mask digits
    text = re.sub(r'\d', 'X', text)
    
    # Mask simple email lookalikes
    text = re.sub(r'\S+@\S+', 'xxx@yyy.com', text)
    
    return text

def analyze_excel(name, path):
    print(f"\n--- Analyzing {name} ---")
    file_path = Path(path).resolve()
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    try:
        # Check suffix safely
        suffix = str(path).lower()
        if suffix.endswith('.xls'):
            engine = 'xlrd'
        else:
            engine = 'openpyxl'
            
        # Inspect first 25 rows to finding headers
        for sheet_name in (pd.ExcelFile(file_path).sheet_names):
             print(f"  Sheet: {sheet_name}")
             df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=25, header=None, engine=engine)
             print("  First 20 rows (Masked):")
             for i, row in df.iterrows():
                 if i > 20: break
                 vals = [str(mask_pii(v))[:20] for v in row.values] # Truncate for display
                 print(f"  Row {i}: {vals}")
        return
            
    except Exception as e:
        print(f"Error reading Excel: {e}")

def analyze_pdf(name, path):
    print(f"\n--- Analyzing {name} ---")
    file_path = Path(path).resolve()
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
        
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                if text:
                    print("\nFirst Page Layout Abstract (Masked):")
                    # Print first 500 chars masked
                    masked_text = mask_pii(text[:1000])
                    print(masked_text + "...")
                else:
                    print("No text extracted (scanned?)")
                    
    except Exception as e:
        print(f"Error reading PDF: {e}")

def main():
    print("Starting Safe Document Analysis...")
    import os
    base_dir = Path(os.getcwd())
    
    for name, relative_path in DOCS.items():
        # Handle path joining robustly
        path = base_dir / relative_path
        if not path.exists() and "wealthwise" not in str(base_dir):
             # Try appending project root if running from wrong dir?
             # Assuming standard layout
             pass 

        if path.suffix.lower() in ['.xls', '.xlsx']:
            analyze_excel(name, path)
        elif path.suffix.lower() == '.pdf':
            analyze_pdf(name, path)

if __name__ == "__main__":
    main()

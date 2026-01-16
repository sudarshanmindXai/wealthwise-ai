import pandas as pd
from pathlib import Path
import random
from datetime import datetime, timedelta

def generate_cas_excel():
    """Generates a synthetic CAS statement in Excel format."""
    
    # Setup data structures
    data = []
    
    schemes = [
        "HDFC Top 100 Fund - Growth Option",
        "SBI Bluechip Fund - Regular Plan Growth",
        "Axis Long Term Equity Fund - Growth",
        "ICICI Prudential Technology Fund - Growth",
        "Parag Parikh Flexi Cap Fund - Direct Growth"
    ]
    
    transaction_types = ["Purchase", "SIP", "Switch In", "Redemption", "Switch Out"]
    
    start_date = datetime(2023, 4, 1)
    
    # Generate transactions
    for _ in range(25):
        date = start_date + timedelta(days=random.randint(1, 365))
        scheme = random.choice(schemes)
        
        # Decide transaction type
        txn_type = random.choice(transaction_types)
        
        amount = 0.0
        units = 0.0
        nav = round(random.uniform(50, 500), 4)
        
        if txn_type in ["Purchase", "SIP", "Switch In"]:
            amount = round(random.uniform(1000, 50000), 2)
            units = round(amount / nav, 3)
        else:
            units = round(random.uniform(10, 100), 3)
            amount = -round(units * nav, 2)
            units = -units
            
        data.append({
            "Folio No": f"101/ {random.randint(100000, 999999)}",
            "Scheme": scheme,
            "Date": date.strftime("%d-%b-%Y"),
            "Transaction Type": txn_type,
            "Amount": amount,
            "Units": units,
            "NAV": nav
        })
        
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Define output path
    base_dir = Path(__file__).resolve().parent.parent / "sample_docs"
    base_dir.mkdir(exist_ok=True)
    output_path = base_dir / "CAS_Rohan_Sharma_Synthetic.xlsx"
    
    # Write to Excel
    df.to_excel(output_path, index=False)
    print(f"Generated synthetic CAS at: {output_path}")
    
    return output_path

if __name__ == "__main__":
    generate_cas_excel()

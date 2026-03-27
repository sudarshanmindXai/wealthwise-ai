
import requests
import time
import os
import csv

# Create a dummy Bank Statement CSV (HDFC style approx)
csv_content = """Date,Description,Debit,Credit,Balance
01/04/2024,UPI-ZEPTO-123456,500.00,0.00,50000.00
02/04/2024,SALARY CR,0.00,100000.00,150000.00
03/04/2024,ZERODHA BROKING,10000.00,0.00,140000.00
"""

with open("tests/dummy_statement.csv", "w") as f:
    f.write(csv_content)

url = "http://localhost:8000/api/v1/ingest/upload"
files = {"file": open("tests/dummy_statement.csv", "rb")}

print(f"Uploading to {url}...")
try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        task_id = data["task_id"]
        print(f"Task ID: {task_id}")
        
        # Poll
        for _ in range(10):
            time.sleep(1)
            status_url = f"http://localhost:8000/api/v1/ingest/status/{task_id}"
            status_res = requests.get(status_url)
            status_data = status_res.json()
            print(f"Poll Status: {status_data.get('status')} | Progress: {status_data.get('progress')}")
            
            if status_data.get("status") == "complete":
                result = status_data.get("result", {})
                txns = result.get("raw_data", {}).get("transactions", [])
                print(f"✅ Success! Found {len(txns)} transactions.")
                for t in txns:
                    print(f" - {t}")
                
                # Check Review Endpoint
                print("\nChecking Review Endpoint...")
                review_res = requests.get("http://localhost:8000/api/v1/review/transactions")
                review_data = review_res.json()
                print(f"Review Items: {len(review_data)}")
                break
            
            elif status_data.get("status") in ["error", "failed"]:
                 print(f"❌ Error: {status_data.get('error')}")
                 break
                 
    else:
        print(f"❌ Upload Failed: {response.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")

finally:
    if os.path.exists("tests/dummy_statement.csv"):
        os.remove("tests/dummy_statement.csv")

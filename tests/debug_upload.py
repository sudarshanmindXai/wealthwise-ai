
import requests
import time
import os

# Create a dummy PDF
with open("tests/dummy.pdf", "wb") as f:
    f.write(b"%PDF-1.4\n%...\nTRAPPED IN A PDF WORLD")

url = "http://localhost:8000/api/v1/ingest/upload"
files = {"file": open("tests/dummy.pdf", "rb")}

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
            
            if status_data.get("status") in ["complete", "error", "failed"]:
                if status_data.get("status") != "complete":
                    print(f"❌ Error Details: {status_data.get('error')}")
                else:
                    print("✅ Success!")
                    print(f"Doc Type: {status_data.get('document_type')}")
                break
    else:
        print(f"❌ Upload Failed: {response.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")

finally:
    if os.path.exists("tests/dummy.pdf"):
        os.remove("tests/dummy.pdf")

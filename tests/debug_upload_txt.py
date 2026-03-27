
import requests
import time
import os

# Create a dummy Text file
with open("tests/dummy.txt", "w") as f:
    f.write("This is a simple rent agreement text.")

url = "http://localhost:8000/api/v1/ingest/upload"
files = {"file": open("tests/dummy.txt", "rb")}

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
                    print(f"Result: {status_data.get('result')}")
                break
    else:
        print(f"❌ Upload Failed: {response.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")

finally:
    if os.path.exists("tests/dummy.txt"):
        os.remove("tests/dummy.txt")

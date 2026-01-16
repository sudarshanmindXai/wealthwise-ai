"""Quick smoke test for /tax/scenarios endpoint"""
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, "f:/wealthwise-ai")
from src.api.app import app

client = TestClient(app)

# Test payload with v2 structure
payload = {
    "profile_version": "v2",
    "assessment_year": "2025-26",
    "tax_facts_input": {
        "assessment_year": "2025-26",
        "residential_status": "resident",
        "age_category": "below_60",
        "salary_gross": 1200000.50,
        "deduction_80c": 100000.25,
        "deduction_80ccd_1b": 25000.00,
        "deduction_80d_self": 15000.75,
        "taxes_tds": 150000.00
    },
    "user_identity": {
        "name": "Test User",
        "pan": "ABCDE1234F"
    }
}

print("📤 POST /tax/scenarios")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

response = client.post("/tax/scenarios", json=payload)

print(f"✅ Status: {response.status_code}")
print(f"📊 Response:\n{json.dumps(response.json(), indent=2)}")

# Check varied savings
data = response.json()
if "top_scenarios" in data:
    print("\n🔍 Checking for varied savings:")
    for scenario in data["top_scenarios"]:
        old_saved = scenario.get("tax_saved_old_regime", 0)
        new_saved = scenario.get("tax_saved_new_regime", 0)
        print(f"  - {scenario['scenario_id']}: Old={old_saved}, New={new_saved}")

from src.api.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

payload = {
    'profile_version': 'v2',
    'assessment_year': '2024-25',
    'tax_facts_input': {
        'salary_gross': 1200000,
        'assessment_year': '2024-25',
        'residential_status': 'resident',
        'age_category': 'below_60'
    },
    'user_identity': {}
}

response = client.post('/tax/scenarios', json=payload)
print('Status:', response.status_code)
print('Response:')
import json
resp_json = response.json()
if response.status_code == 200:
    print(f"Scenarios: {len(resp_json.get('top_scenarios', []))} top scenarios found")
    print(f"Recommended regime: {resp_json.get('recommended_regime')}")
else:
    print(f"Error: {resp_json.get('detail')}")

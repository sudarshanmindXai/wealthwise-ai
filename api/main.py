from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
import os
import sys

# Add root to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing logic (mocking for now to ensure server starts without dependencies issues)
# from src.ingest.universal_extractor import extract_document_data
# from src.calculators.tax_engine import calculate_tax

app = FastAPI(title="WealthWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "WealthWise API"}

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    # Mock response for UI testing
    return {
        "filename": file.filename,
        "status": "processed",
        "data": {
            "gross_salary": 2450000,
            "tds_paid": 280000,
            "confidence": 0.98
        }
    }

@app.post("/calculate")
def calculate_tax(profile: Dict[str, Any]):
    # Mock calculation based on profile
    # real logic would call src/calculators
    return {
        "old_regime": {"tax": 450000},
        "new_regime": {"tax": 420000},
        "savings": 30000,
        "recommendation": "NEW"
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

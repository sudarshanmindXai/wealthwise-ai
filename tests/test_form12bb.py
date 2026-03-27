import sys
import os
import pytest
from api.output.form12bb import Form12BBGenerator

@pytest.fixture
def sample_data():
    return {
        "user": {
            "name": "Rohan Patel",
            "address": "Flat 402, Oakwood Residency, Indiranagar, Bangalore - 560038",
            "pan": "ABCDE1234F",
            "father_name": "Suresh Patel",
            "designation": "Senior Software Engineer",
            "financial_year": "2025-26"
        },
        "hra": {
            "rent_paid": 180000,
            "landlord_name": "Amit Kumar",
            "landlord_pan": "FGHIJ5678K",
            "address": "Flat 402, Oakwood Residency, Indiranagar, Bangalore"
        },
        "lta": 45000,
        "home_loan_interest": {
            "amount": 200000,
            "lender_name": "HDFC Bank",
            "lender_pan": "HDFC000123"
        },
        "deductions_80c": [
            {"description": "EPF", "amount": 100000},
            {"description": "PPF", "amount": 50000}
        ],
        "deductions_points": {
            "80D": 25000,
            "80G": 10000
        }
    }

def test_generate_form12bb_pdf(sample_data):
    generator = Form12BBGenerator(sample_data)
    pdf_bytes = generator.generate()
    
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")

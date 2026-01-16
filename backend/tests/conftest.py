"""
WealthWise AI - Test Configuration
"""

import pytest
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def sample_rohan_profile():
    """Rohan Sharma's test profile from test_scenarios.md"""
    return {
        "name": "Rohan Sharma",
        "pan": "ABCRS1234P",
        "fy": "2025-26",
        "income": {
            "salary": {
                "gross": 1800000,
                "basic": 900000,
                "hra_received": 300000,
                "tds": 180000
            },
            "freelance": {
                "receipts": 600000,
                "expenses": 150000
            },
            "investments": {
                "ltcg_realized": 80000,
                "stcg_realized": 0
            }
        },
        "deductions_claimed": {
            "80c": 150000,
            "80d": 25000
        },
        "rent_paid_annual": 240000,
        "city": "Bangalore",
        "metro": True,
    }


@pytest.fixture
def tax_calculator():
    """Provides a TaxCalculator instance"""
    from app.engine.calculator import calculate_tax
    return calculate_tax


@pytest.fixture
def tolerance():
    """₹10 tolerance per test_scenarios.md"""
    return 10

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


VALID_PROFILE = {
    "profile_version": "v1",
    "assessment_year": "2024-25",
    "taxpayer": {
        "age": 30,
        "residential_status": "resident"
    },
    "income": {
        "salary": 1200000,
        "other_income": 0,
        "deductions": {
            "section_80c": 150000
        }
    },
    "flags": {
        "is_senior_citizen": False
    }
}


def test_tax_recommendation_happy_path():
    response = client.post(
        "/tax/recommendation",
        json=VALID_PROFILE
    )

    assert response.status_code == 200
    body = response.json()

    assert body["itr"]["recommended"] == "ITR-1"
    assert body["regime"]["recommended"] in ["OLD", "NEW"]
    assert "income_breakup" in body
    assert body["income_breakup"]["gross_total_income"] == 1200000
    assert body["income_breakup"]["taxable_income_old_regime"] > 0
    assert isinstance(body["explanation"]["bullets"], list)


def test_tax_chat_happy_path():
    response = client.post(
        "/tax/chat",
        json={
            "user_message": "Which ITR should I file?",
            "profile": VALID_PROFILE
        }
    )

    assert response.status_code == 200
    body = response.json()

    assert body["intent"] == "tax_recommendation"
    assert body["recommendation"]["itr"]["recommended"] == "ITR-1"
    assert "disclaimer" in body


def test_tax_recommendation_validation_error():
    """
    Schema validation errors are handled by FastAPI/Pydantic
    and correctly return HTTP 422.
    """
    invalid_profile = {
        "profile_version": "v1",
        "assessment_year": "2024-25",
        "income": {
            "salary": 1200000
        },
        "flags": {}
    }

    response = client.post(
        "/tax/recommendation",
        json=invalid_profile
    )

    assert response.status_code == 422
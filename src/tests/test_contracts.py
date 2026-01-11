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


def test_tax_recommendation_output_contract():
    response = client.post(
        "/tax/recommendation",
        json=VALID_PROFILE
    )

    assert response.status_code == 200
    body = response.json()

    # ---- Top-level keys ----
    assert set(body.keys()) == {
        "itr",
        "regime",
        "income_breakup",
        "explanation",
        "missing_info",
        "followup_questions",
        "citations",
    }

    # ---- ITR ----
    assert "recommended" in body["itr"]
    assert isinstance(body["itr"]["reasons"], list)

    # ---- Regime ----
    assert body["regime"]["recommended"] in ["OLD", "NEW"]
    assert isinstance(body["regime"]["old_tax"], (int, float))
    assert isinstance(body["regime"]["new_tax"], (int, float))

    # ---- Income breakup ----
    ib = body["income_breakup"]
    assert isinstance(ib["gross_total_income"], (int, float))
    assert isinstance(ib["total_deductions_old_regime"], (int, float))
    assert isinstance(ib["taxable_income_old_regime"], (int, float))

    # ---- Explanation ----
    exp = body["explanation"]
    assert isinstance(exp["bullets"], list)
    assert isinstance(exp["user_friendly"], str)

    # ---- Missing info ----
    mi = body["missing_info"]
    assert set(mi.keys()) == {"required", "optional"}
    assert isinstance(mi["required"], list)
    assert isinstance(mi["optional"], list)

    # ---- Followups ----
    assert isinstance(body["followup_questions"], list)

    # ---- Citations ----
    assert isinstance(body["citations"], list)
    if body["citations"]:
        c = body["citations"][0]
        assert set(c.keys()) == {
            "doc_id",
            "file",
            "line_no",
            "text_preview",
        }


def test_tax_chat_output_contract():
    response = client.post(
        "/tax/chat",
        json={
            "user_message": "Which ITR should I file?",
            "profile": VALID_PROFILE
        }
    )

    assert response.status_code == 200
    body = response.json()

    # ---- Top-level ----
    assert set(body.keys()) == {
        "intent",
        "recommendation",
        "disclaimer",
    }

    assert body["intent"] == "tax_recommendation"
    assert isinstance(body["disclaimer"], str)

    rec = body["recommendation"]

    # ---- Recommendation mirrors /tax/recommendation ----
    assert "itr" in rec
    assert "regime" in rec
    assert "income_breakup" in rec
    assert "explanation" in rec
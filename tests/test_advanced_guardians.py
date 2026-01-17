
import pytest
from api.guardians.base import UserContext
from api.guardians.salary import SalarySentinel
from api.guardians.portfolio import PortfolioArchitect
from api.guardians.hustle import HustleShield
from api.guardians.windfall import WindfallWarden

def test_salary_ev_lease():
    sentinel = SalarySentinel()
    context = UserContext(
        user_id="test",
        income_salary=2500000, # High salary
        is_ev_owner=False
    )
    insights = sentinel.analyze(context)
    ev_insights = [i for i in insights if "EV Corporate Lease" in i.title]
    assert len(ev_insights) > 0
    assert ev_insights[0].category == "deduction"

def test_portfolio_crypto_loss():
    architect = PortfolioArchitect()
    context = UserContext(
        user_id="test",
        has_crypto_losses=True
    )
    insights = architect.analyze(context)
    crypto_warnings = [i for i in insights if "Crypto Loss Trap" in i.title]
    assert len(crypto_warnings) > 0
    assert crypto_warnings[0].category == "warning"

def test_hustle_gst_warning():
    shield = HustleShield()
    context = UserContext(
        user_id="test",
        income_business=2200000, # > 20L
        turnover_business=2200000
    )
    insights = shield.analyze(context)
    gst_warnings = [i for i in insights if "GST Registration" in i.title]
    assert len(gst_warnings) > 0
    
def test_windfall_rent_deduction():
    warden = WindfallWarden()
    context = UserContext(
        user_id="test",
        income_rent_received=500000
    )
    insights = warden.analyze(context)
    deductions = [i for i in insights if "Rental Income Standard Deduction" in i.title]
    assert len(deductions) > 0
    assert deductions[0].impact_currency == (500000 * 0.30) * 0.30 # Deduction * Rate

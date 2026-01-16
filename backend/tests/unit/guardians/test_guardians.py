"""
WealthWise AI - Guardian Tests
Validates: Salary Sentinel, Portfolio Architect, Hustle Shield, Windfall Warden
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.guardians import (
    SalarySentinel,
    PortfolioArchitect,
    HustleShield,
    WindfallWarden,
)


class TestSalarySentinel:
    """Tests for Salary Sentinel Guardian"""

    def test_ss01_nps_under_utilized(self):
        """SS-01: NPS under-utilized detection"""
        sentinel = SalarySentinel()
        
        result = sentinel.analyze({
            'basic': 1000000,
            'employer_nps': 0,
        })
        
        findings = [f.code for f in result.findings]
        assert 'NPS_UNDERUTILIZED' in findings, \
            "Should detect NPS under-utilization"
        
        # Should recommend adding ₹1.4L (14% of basic)
        nps_finding = next(f for f in result.findings if f.code == 'NPS_UNDERUTILIZED')
        assert nps_finding.potential_savings > 0

    def test_ss02_ev_opportunity(self):
        """SS-02: EV lease opportunity detection"""
        sentinel = SalarySentinel()
        
        result = sentinel.analyze({
            'gross_salary': 3000000,  # 30% slab
            'car_emi': 30000,
            'has_car_benefit': False,
        })
        
        findings = [f.code for f in result.findings]
        # Should recommend EV lease for high earners
        assert 'EV_LEASE_OPPORTUNITY' in findings, \
            "Should detect EV lease opportunity for 30% slab"

    def test_ss03_hra_claim_possible(self):
        """SS-03: HRA exemption opportunity"""
        sentinel = SalarySentinel()
        
        result = sentinel.analyze({
            'basic': 900000,
            'hra_received': 300000,
            'rent_paid': 300000,  # ₹25K/month
            'hra_claimed': 0,
            'metro': True,
        })
        
        findings = [f.code for f in result.findings]
        assert 'HRA_UNCLAIMED' in findings, \
            "Should detect unclaimed HRA opportunity"


class TestPortfolioArchitect:
    """Tests for Portfolio Architect Guardian"""

    def test_pa01_loss_harvesting(self):
        """PA-01: Loss harvesting opportunity"""
        architect = PortfolioArchitect()
        
        result = architect.analyze({
            'ltcg_unrealized': 100000,
            'realized_ltcg_ytd': 0,
        })
        
        findings = [f.code for f in result.findings]
        assert 'HARVESTING_OPPORTUNITY' in findings, \
            "Should detect tax-free LTCG harvesting opportunity"

    def test_pa02_buyback_warning(self):
        """PA-02: Buyback vs market sale"""
        architect = PortfolioArchitect()
        
        result = architect.analyze({
            'marginal_rate': 0.30,  # 30% bracket
            'has_buyback_offer': True,
            'holding_period': 'long',
        })
        
        findings = [f.code for f in result.findings]
        assert 'BUYBACK_WARNING' in findings, \
            "Should warn against buyback for high slab taxpayers"

    def test_pa03_crypto_isolation(self):
        """PA-03: Crypto losses cannot be set off"""
        architect = PortfolioArchitect()
        
        result = architect.analyze({
            'crypto_losses': 50000,
            'salary_income': 1500000,
        })
        
        findings = [f.code for f in result.findings]
        assert 'CRYPTO_LOSS_DEAD' in findings, \
            "Should warn that crypto losses cannot offset other income"


class TestHustleShield:
    """Tests for Hustle Shield Guardian (44ADA)"""

    def test_hs01_44ada_eligible(self):
        """HS-01: 44ADA eligibility check"""
        shield = HustleShield()
        
        result = shield.analyze({
            'receipts': 5000000,  # ₹50L
            'actual_expenses': 1000000,  # 20% of receipts (High profit margin)
            'profession': 'technical_consultancy',
        })
        
        assert result.metadata['is_44ada_eligible'] == True, \
            "Should be 44ADA eligible for receipts ≤ ₹75L"
        
        findings = [f.code for f in result.findings]
        assert '44ADA_APPLICABLE' in findings, \
            "Should recommend 44ADA when beneficial"

    def test_hs02_over_limit(self):
        """HS-02: 44ADA not allowed for receipts > ₹75L"""
        shield = HustleShield()
        
        result = shield.analyze({
            'receipts': 8000000,  # ₹80L
        })
        
        assert result.metadata['is_44ada_eligible'] == False, \
            "Should NOT be 44ADA eligible for receipts > ₹75L"
        
        findings = [f.code for f in result.findings]
        assert 'REQUIRES_AUDIT' in findings, \
            "Should flag audit requirement"


class TestWindfallWarden:
    """Tests for Windfall Warden Guardian"""

    def test_ww01_rent_optimization(self):
        """WW-01: Rent standard deduction"""
        warden = WindfallWarden()
        
        result = warden.analyze({
            'rental': {
                'rent_received': 500000,  # ₹5L
            }
        })
        
        # Should recommend 30% standard deduction
        # Should recommend 30% standard deduction
        rental_finding = next(f for f in result.findings if f.code == 'RENTAL_SECTION_24')
        assert rental_finding, "Should find rental section 24 finding"
        assert result.metadata['rental_taxable'] == 350000, \
            "Taxable HP income should be ₹3.5L after 30% deduction"

    def test_ww02_gift_taxable(self):
        """WW-02: Gift from friend is taxable"""
        warden = WindfallWarden()
        
        result = warden.analyze({
            'gifts': [
                {'amount': 100000, 'relation': 'friend'},
            ]
        })
        
        findings = [f.code for f in result.findings]
        assert 'GIFT_TAXABLE' in findings, \
            "Gift from friend (>₹50K) should be taxable"

    def test_ww03_gift_exempt(self):
        """WW-03: Gift from parent is exempt"""
        warden = WindfallWarden()
        
        result = warden.analyze({
            'gifts': [
                {'amount': 100000, 'relation': 'parent'},
            ]
        })
        
        findings = [f.code for f in result.findings]
        assert 'GIFT_EXEMPT_RELATIVE' in findings, \
            "Gift from parent (linear ascendant) should be exempt"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

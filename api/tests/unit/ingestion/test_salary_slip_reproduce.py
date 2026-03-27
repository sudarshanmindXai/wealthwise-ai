import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from api.ingestion.parsers.salary_slip import SalarySlipParser

class TestSalarySlipReproduction:
    
    @pytest.fixture
    def parser(self):
        return SalarySlipParser()

    @pytest.fixture
    def problematic_text(self):
        return """
User Experience Design Consulting Private Limited
Pay Slip
for May-2021
Siddhant Jha
Employee Number : UXDC-062
...
Earnings Amount Deductions Amount
Basic Salary 59,028.00 Professional Tax Payable 200.00
House Rent Allowance 23,611.00 TDS on Salaries 13,442.00
...
Total Earnings 1,18,055.00 Total Deductions 20,081.00
Net Amount (cid:299) 97,974.00
Amount (in words):
Indian Rupees Ninety Seven Thousand Nine Hundred Seventy Four
Only
"""

    def test_parse_failed_salary_slip(self, parser, problematic_text):
        """Test parsing with text similar to the failed upload"""
        
        # Mock _extract_text, validate_file AND compute_file_hash
        with patch.object(SalarySlipParser, '_extract_text', return_value=(problematic_text, 1)), \
             patch.object(SalarySlipParser, 'validate_file', return_value=(True, None)), \
             patch.object(SalarySlipParser, 'compute_file_hash', return_value="dummy_hash"):
            
            # We can pass any path since we mocked extraction
            result = parser.parse(Path("dummy_path.pdf"))
            
            # This should currently FAIL or have missing net_pay
            # net_pay should be 97,974.00
            
            fields = {f.name: f.value for f in result.fields}
            
            print(f"Extracted fields: {fields}")
            if result.errors:
                 print(f"Errors: {result.errors}")

            assert "net_pay" in fields
            assert fields["net_pay"] == 97974.00, f"Expected 97974.0, got {fields.get('net_pay')}"

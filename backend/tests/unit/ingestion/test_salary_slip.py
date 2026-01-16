import pytest
from pathlib import Path
from unittest.mock import patch
from app.ingestion.parsers.salary_slip import SalarySlipParser, DocumentType

class TestSalarySlipParser:
    
    @pytest.fixture
    def parser(self):
        return SalarySlipParser()
    
    @pytest.fixture
    def sample_pdf(self):
        # Locate the generated sample PDF
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        return (base_dir / "sample_docs/salary_slip_vikram.pdf").resolve()

    def test_parse_real_salary_slip(self, parser, sample_pdf):
        """Test parsing the generated sample Salary Slip"""
        if not sample_pdf.exists():
            pytest.skip(f"Sample PDF not found at {sample_pdf}")

        result = parser.parse(sample_pdf)

        assert result.success is True
        assert result.document_type == DocumentType.SALARY_SLIP

        # Check extracted fields
        fields = {f.name: f.value for f in result.fields}
        
        # Verify values from the generated PDF (generate_salary_slip.py)
        # Net Pay: 2,77,800.00
        assert fields["net_pay"] == 277800.0
        # Basic: 1,50,000.00
        assert fields["basic_salary"] == 150000.0
        # HRA: 75,000.00
        assert fields["hra"] == 75000.0
        # PF: 12,000.00
        assert fields["pf_deduction"] == 12000.0
        # TDS: 85,000.00
        assert fields["tds_deduction"] == 85000.0
        # PAN: ABCDE1234F
        assert "ABCDE1234F" in fields["pan"]
        
        # Verify PII Scrubbing
        scrubbed = result.raw_data.get("scrubbed_text", "")
        if scrubbed:
            assert "ABCDE1234F" not in scrubbed, "PAN should be scrubbed"
            assert "XXXXX1234X" in scrubbed, "Masked PAN should be present"

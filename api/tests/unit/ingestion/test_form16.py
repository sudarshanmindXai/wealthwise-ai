"""
Tests for Form 16 Parser
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from api.ingestion.parsers.form16 import Form16Parser
from api.ingestion.parsers.base import DocumentType

class TestForm16Parser:
    
    @pytest.fixture
    def parser(self):
        return Form16Parser()
    
    def test_parse_real_form16(self, parser):
        """Test parsing the generated sample Form 16"""
        # Path to generated sample
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
            
        file_path = (base_dir / "sample_docs/form16_vikram.pdf").resolve()
        
        if not file_path.exists():
            pytest.skip(f"Sample Form 16 not found at {file_path}")
            
        result = parser.parse(file_path)
        
        assert result.success is True
        assert result.document_type == DocumentType.FORM_16
        
        # Check extracted fields
        fields = {f.name: f.value for f in result.fields}
        
        # Verify specific values from the generated PDF
        assert fields["gross_salary"] == 4500000.0
        assert fields["hra"] == 300000.0
        assert fields["standard_deduction"] == 50000.0
        # Tax deducted matches tax payable in our generated form
        assert fields["tds_deducted"] == 979451.0 
        assert "TechNova Solutions" in fields["employer_name"]
        
        # Verify PII scrubbing in raw_data
        scrubbed = result.raw_data.get("scrubbed_content", "")
        if scrubbed:
            assert "ABCDE1234F" not in scrubbed, "PAN should be scrubbed from raw data"
            assert "XXXXX1234X" in scrubbed, "Masked PAN should be present"
        
    @patch("pdfplumber.open")
    def test_detect_form16(self, mock_pdfplumber_open, parser):
        # Mock PDF content
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "FORM NO. 16 Part B Certificate under section 203"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf
        
        file_path = Path("form16.pdf")
        
        is_match, confidence = parser.detect(file_path)
        assert is_match is True
        assert confidence > 0.5

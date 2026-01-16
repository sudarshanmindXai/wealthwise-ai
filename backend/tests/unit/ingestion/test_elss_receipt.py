import pytest
from pathlib import Path
from app.ingestion.parsers.elss_receipt import ELSSReceiptParser, DocumentType

class TestELSSReceiptParser:
    
    @pytest.fixture
    def parser(self):
        return ELSSReceiptParser()
    
    @pytest.fixture
    def sample_pdf(self):
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        return (base_dir / "sample_docs/elss_receipt_vikram.pdf").resolve()

    def test_parse_real_elss_receipt(self, parser, sample_pdf):
        """Test parsing the generated sample ELSS Receipt"""
        if not sample_pdf.exists():
            pytest.skip(f"Sample PDF not found at {sample_pdf}")

        result = parser.parse(sample_pdf)

        assert result.success is True
        assert result.document_type == DocumentType.ELSS_RECEIPT
        
        # Check Fields
        # We generated 3 txns of 50k each -> Total 1.5L
        
        # Check raw transactions
        txns = result.raw_data.get("transactions", [])
        assert len(txns) >= 3
        
        # Verify amounts
        total_amount = sum(t["amount"] for t in txns if t["amount"])
        assert total_amount == 150000.0
        
        # Check extracted field for total
        total_field = next((f for f in result.fields if f.name == "total_elss_investment"), None)
        assert total_field is not None
        assert total_field.value == 150000.0
        
        # Verify PII Scrubbing
        scrubbed = result.raw_data.get("scrubbed_text", "")
        if scrubbed:
            assert "ABCDE1234F" not in scrubbed, "PAN should be scrubbed"
            assert "XXXXX1234X" in scrubbed, "Masked PAN should be present"

import pytest
from pathlib import Path
from app.ingestion.parsers.bank_statement import BankStatementParser, DocumentType

class TestBankStatementParser:
    
    @pytest.fixture
    def parser(self):
        return BankStatementParser()
    
    @pytest.fixture
    def sample_csv(self):
        # Locate the generated sample CSV
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        return (base_dir / "sample_docs/bank_statement_vikram.csv").resolve()

    @pytest.fixture
    def sample_xlsx(self):
        # Locate the generated sample XLSX
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        return (base_dir / "sample_docs/bank_statement_vikram.xlsx").resolve()

    def test_detect_csv(self, parser, sample_csv):
        if not sample_csv.exists():
            pytest.skip("Sample CSV not found")
            
        is_match, confidence = parser.detect(sample_csv)
        assert is_match is True
        assert confidence > 0.5
        
    def test_detect_xlsx(self, parser, sample_xlsx):
        if not sample_xlsx.exists():
            pytest.skip("Sample XLSX not found")
            
        is_match, confidence = parser.detect(sample_xlsx)
        assert is_match is True
        assert confidence > 0.5
        
    def test_parse_csv(self, parser, sample_csv):
        if not sample_csv.exists():
            pytest.skip("Sample CSV not found")
            
        result = parser.parse(sample_csv)
        
        assert result.success is True
        assert result.document_type == DocumentType.BANK_STATEMENT
        
        # Check basic fields
        fields = {f.name: f.value for f in result.fields}
        assert fields["transaction_count"] == 150
        assert fields["total_credits"] > 0
        assert fields["total_debits"] > 0
        
        # Verify PII Scrubbing in raw data
        raw_txns = result.raw_data["transactions"]
        for txn in raw_txns:
            desc = txn["description"]
            # Phone numbers should be masked
            if "9876543210" in desc:
                 pytest.fail(f"PII Leak found: {desc}")
            # Check for masked format if it was a PII transaction
            if "Transfer to" in desc and "XXXXXXXXXX" in desc:
                pass # Verified masked
                
    def test_parse_xlsx(self, parser, sample_xlsx):
        if not sample_xlsx.exists():
            pytest.skip("Sample XLSX not found")
            
        result = parser.parse(sample_xlsx)
        assert result.success is True
        assert len(result.raw_data["transactions"]) == 150

    def test_categorization(self, parser, sample_csv):
        if not sample_csv.exists():
            pytest.skip("Sample CSV not found")
            
        result = parser.parse(sample_csv)
        raw_txns = result.raw_data["transactions"]
        
        # Check specific known categories
        personal_txns = [t for t in raw_txns if "Swiggy" in t["description"] or "Zomato" in t["description"]]
        for t in personal_txns:
            assert t["category"] == "personal" or t["category"] == "ambiguous" # Ambiguous if amt > 50k (unlikely for food but possible in sim)
            
        business_txns = [t for t in raw_txns if "Razorpay" in t["description"]]
        for t in business_txns:
            assert t["category"] == "business" or t["category"] == "ambiguous"

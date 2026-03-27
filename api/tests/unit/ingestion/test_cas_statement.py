import pytest
from pathlib import Path
from api.ingestion.parsers.cas_statement import CASStatementParser, DocumentType

class TestCASStatementParser:
    
    @pytest.fixture
    def parser(self):
        return CASStatementParser()
    
    @pytest.fixture
    def sample_cas_file(self):
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        
        # Path where generator creates the file
        path = (base_dir / "sample_docs/CAS_Rohan_Sharma_Synthetic.xlsx").resolve()
        return path

    def test_detect_cas_statement(self, parser, sample_cas_file):
        """Test detection of CAS statement"""
        if not sample_cas_file.exists():
            pytest.skip(f"Sample CAS file not found at {sample_cas_file}. Run generation script first.")
            
        is_match, confidence = parser.detect(sample_cas_file)
        assert is_match is True
        assert confidence > 0.8

    def test_parse_cas_statement(self, parser, sample_cas_file):
        """Test parsing of CAS statement"""
        if not sample_cas_file.exists():
            pytest.skip(f"Sample CAS file not found at {sample_cas_file}")

        result = parser.parse(sample_cas_file)

        assert result.success is True
        assert result.document_type == DocumentType.CAS_STATEMENT
        
        # Check Fields
        total_txns = next((f.value for f in result.fields if f.name == "total_transactions"), 0)
        unique_schemes = next((f.value for f in result.fields if f.name == "unique_schemes_count"), 0)
        
        assert total_txns == 25 # We generated 25 transactions
        assert unique_schemes > 0
        
        # Check raw transactions
        txns = result.raw_data.get("transactions", [])
        assert len(txns) == 25
        
        # Validate structure of a transaction
        txn = txns[0]
        assert "scheme" in txn
        assert "folio" in txn
        assert "amount" in txn
        assert "units" in txn
        assert "type" in txn

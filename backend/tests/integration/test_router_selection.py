import pytest
from pathlib import Path
from app.ingestion.router import get_parser_for_file
from app.ingestion.parsers import (
    Form16Parser,
    BankStatementParser,
    SalarySlipParser,
    ELSSReceiptParser,
    ZerodhaPnLParser
)

class TestRouterSelection:
    
    @pytest.fixture
    def sample_dir(self):
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        return (base_dir / "sample_docs").resolve()

    def test_select_form16(self, sample_dir):
        f = sample_dir / "form16_vikram.pdf"
        if not f.exists(): pytest.skip("Sample not found")
        
        parser = get_parser_for_file(f)
        assert isinstance(parser, Form16Parser)

    def test_select_bank_statement_xlsx(self, sample_dir):
        f = sample_dir / "bank_statement_vikram.xlsx"
        if not f.exists(): pytest.skip("Sample not found")
        
        parser = get_parser_for_file(f)
        assert isinstance(parser, BankStatementParser)
        
    def test_select_bank_statement_csv(self, sample_dir):
        f = sample_dir / "bank_statement_vikram.csv" # ICICI
        if not f.exists(): pytest.skip("Sample not found")
        
        parser = get_parser_for_file(f)
        assert isinstance(parser, BankStatementParser)

    def test_select_salary_slip(self, sample_dir):
        f = sample_dir / "salary_slip_vikram.pdf"
        if not f.exists(): pytest.skip("Sample not found")
        
        parser = get_parser_for_file(f)
        assert isinstance(parser, SalarySlipParser)

    def test_select_elss_receipt(self, sample_dir):
        f = sample_dir / "elss_receipt_vikram.pdf"
        if not f.exists(): pytest.skip("Sample not found")
        
        # ELSS works by heuristic content match
        parser = get_parser_for_file(f)
        assert isinstance(parser, ELSSReceiptParser)
        
    def test_select_zerodha_pnl(self, sample_dir):
        f = sample_dir / "Zerodha_pnl_vikram.xlsx"
        if not f.exists(): pytest.skip("Sample not found")
        
        parser = get_parser_for_file(f)
        assert isinstance(parser, ZerodhaPnLParser)

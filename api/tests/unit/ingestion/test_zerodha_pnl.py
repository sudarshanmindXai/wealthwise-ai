import pytest
from pathlib import Path
from api.ingestion.parsers.zerodha_pnl import ZerodhaPnLParser, DocumentType

class TestZerodhaPnLParser:
    
    @pytest.fixture
    def parser(self):
        return ZerodhaPnLParser()
    
    @pytest.fixture
    def sample_xlsx(self):
        import os
        base_dir = Path(os.getcwd())
        if "backend" not in str(base_dir):
            base_dir = base_dir / "wealthwise/backend"
        return (base_dir / "sample_docs/Zerodha_pnl_vikram.xlsx").resolve()

    def test_parse_real_zerodha_pnl(self, parser, sample_xlsx):
        """Test parsing the generated Zerodha P&L"""
        if not sample_xlsx.exists():
            pytest.skip(f"Sample XLSX not found at {sample_xlsx}")

        result = parser.parse(sample_xlsx)

        assert result.success is True
        assert result.document_type == DocumentType.ZERODHA_PNL
        
        # Check Fields
        total_pnl = next((f.value for f in result.fields if f.name == "total_realized_profit"), None)
        total_div = next((f.value for f in result.fields if f.name == "total_dividends"), None)
        
        assert total_pnl is not None
        assert total_div is not None
        
        # We generated 6 stocks for P&L and 3 stocks for Dividends.
        # Check raw transactions
        txns = result.raw_data.get("transactions", [])
        assert len(txns) >= 9 # 6 trades + 3 dividends
        
        # Check types
        equity_trades = [t for t in txns if t["type"] == "equity_trade"]
        dividends = [t for t in txns if t["type"] == "dividend"]
        
        assert len(equity_trades) >= 6
        assert len(dividends) >= 3
        
        # Verify columns exist
        curr_trade = equity_trades[0]
        assert "symbol" in curr_trade
        assert "profit" in curr_trade
        
        curr_div = dividends[0]
        assert "symbol" in curr_div
        assert "amount" in curr_div
        assert "date" in curr_div

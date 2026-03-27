from pathlib import Path
import pandas as pd
from typing import Optional
import time

from .base import (
    BaseParser,
    ParseResult,
    ExtractionField,
    DocumentType,
)

class ZerodhaPnLParser(BaseParser):
    """
    Parser for Zerodha Tax P&L (XLSX).
    
    Extracts:
    - Realized Profit (Equity)
    - Dividends (Equity)
    - Client Info (Metadata)
    """
    
    DOCUMENT_TYPE = DocumentType.ZERODHA_PNL
    SUPPORTED_EXTENSIONS = [".xlsx"]
    
    SHEET_MAPPINGS = {
        "equity": ["equity"],
        "dividends": ["equity dividends", "dividends"], 
    }
    
    COLUMN_MAPPINGS = {
        "symbol": ["symbol", "scrip"],
        "isin": ["isin"],
        "quantity": ["quantity", "qty"],
        "buy_value": ["buy value"],
        "sell_value": ["sell value"],
        "profit": ["realized profit", "profit/loss", "net profit"],
        "date": ["date"],
        "amount": ["net dividend amount", "amount"], # For dividends
    }

    def detect(self, file_path: Path) -> tuple[bool, float]:
        """Detect if file is Zerodha P&L"""
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False, 0.0
            
        try:
            # Check sheet names first (fast)
            xl = pd.ExcelFile(file_path)
            sheet_names = [s.lower() for s in xl.sheet_names]
            
            # Zerodha typical sheets: "Equity", "Equity Dividends", "F&O"
            if "equity" in sheet_names:
                # Check content of first sheet slightly
                df = pd.read_excel(file_path, sheet_name=0, nrows=20, header=None)
                # Look for "Zerodha" or "Tax P&L" or "Realized Profit"
                # Actually Zerodha Excel usually just starts with Client ID or "Realized Profit Breakdown"
                
                content = df.to_string().lower()
                if "realized profit" in content or "client id" in content:
                    return True, 0.95
                    
            return False, 0.0
        except Exception:
            return False, 0.0

    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """Find row with 'Symbol' and 'ISIN' logic"""
        # Look in first 20 rows
        for i in range(min(20, len(df))):
            row_str = " ".join([str(val).lower() for val in df.iloc[i].values])
            if "symbol" in row_str and "isin" in row_str:
                return i
        return None

    def _parse_equity_sheet(self, df: pd.DataFrame) -> list[dict]:
        header_idx = self._find_header_row(df)
        if header_idx is None:
            return []
            
        # Reload with header
        # Actually extracting based on index is easier, 
        # but let's just slice and set header
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx+1:].reset_index(drop=True)
        
        # Normalize columns
        cols = {str(c).lower().strip(): c for c in df.columns}
        
        # Helpers
        def get_col(mapping_key):
            for pattern in self.COLUMN_MAPPINGS[mapping_key]:
                for c in cols:
                    if pattern in c:
                        return cols[c]
            return None
        
        sym_col = get_col("symbol")
        profit_col = get_col("profit")
        
        txns = []
        if sym_col and profit_col:
            for _, row in df.iterrows():
                try:
                    sym = row[sym_col]
                    profit = row[profit_col]
                    
                    if pd.isna(sym) or pd.isna(profit):
                        continue
                        
                    txns.append({
                        "symbol": str(sym),
                        "profit": float(profit) if isinstance(profit, (int, float)) else 0.0,
                        "type": "equity_trade"
                    })
                except Exception:
                    continue
                    
        return txns

    def _parse_dividend_sheet(self, df: pd.DataFrame) -> list[dict]:
        header_idx = self._find_header_row(df)
        if header_idx is None:
            return []
            
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx+1:].reset_index(drop=True)
        
        # Normalize
        cols = {str(c).lower().strip(): c for c in df.columns}
        
        def get_col(mapping_key):
            for pattern in self.COLUMN_MAPPINGS[mapping_key]:
                for c in cols:
                    if pattern in c:
                        return cols[c]
            return None
            
        sym_col = get_col("symbol")
        amt_col = get_col("amount")
        date_col = get_col("date")
        
        txns = []
        if sym_col and amt_col:
            for _, row in df.iterrows():
                try:
                    amt = row[amt_col]
                    if pd.isna(amt):
                        continue
                        
                    txns.append({
                        "symbol": str(row.get(sym_col, "")),
                        "amount": float(amt),
                        "date": str(row.get(date_col, "")),
                        "type": "dividend"
                    })
                except Exception:
                    continue
        return txns

    def parse(self, file_path: Path) -> ParseResult:
        start_time = time.time()
        
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            return ParseResult(
                success=False, 
                document_type=self.DOCUMENT_TYPE, 
                file_hash="",
                errors=[error]
            )
            
        try:
            xl = pd.ExcelFile(file_path)
            # Find relevant sheets
            equity_sheet = next((s for s in xl.sheet_names if "equit" in s.lower() and "div" not in s.lower()), None)
            div_sheet = next((s for s in xl.sheet_names if "dividend" in s.lower()), None)
            
            raw_txns = []
            fields = []
            
            # Parse Equity
            if equity_sheet:
                df_eq = pd.read_excel(file_path, sheet_name=equity_sheet, header=None) # Read without header first
                eq_txns = self._parse_equity_sheet(df_eq)
                raw_txns.extend(eq_txns)
                
                total_profit = sum(t["profit"] for t in eq_txns)
                fields.append(ExtractionField(name="total_realized_profit", value=total_profit, confidence=0.9))
                
            # Parse Dividends
            if div_sheet:
                df_div = pd.read_excel(file_path, sheet_name=div_sheet, header=None)
                div_txns = self._parse_dividend_sheet(df_div)
                raw_txns.extend(div_txns)
                
                total_div = sum(t["amount"] for t in div_txns)
                fields.append(ExtractionField(name="total_dividends", value=total_div, confidence=0.9))
            
            success = len(raw_txns) > 0
            
            return ParseResult(
                success=success,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={
                    "transactions": raw_txns,
                    "sheet_names": xl.sheet_names
                },
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            return ParseResult(
                success=False, 
                document_type=self.DOCUMENT_TYPE, 
                file_hash="",
                errors=[str(e)]
            )

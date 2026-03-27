import re
import pandas as pd
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
from .base import BaseParser, DocumentType, ParseResult, ExtractionField

class CASStatementParser(BaseParser):
    """
    Parser for Consolidated Account Statements (CAS) from CAMS/KFintech.
    Currently supports Excel format.
    """
    
    DOCUMENT_TYPE = DocumentType.CAS_STATEMENT
    SUPPORTED_EXTENSIONS = [".xlsx", ".xls", ".csv"]
    
    def detect(self, file_path: Path) -> tuple[bool, float]:
        """
        Detect if file is a CAS statement.
        Checks for columns like "Folio No", "Scheme Name", "NAV", "Units".
        """
        try:
            # Quick check for extension
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return False, 0.0
                
            # Read first few rows to check headers
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path, nrows=20)
            else:
                df = pd.read_excel(file_path, nrows=20)
            
            # Convert to string and lowercase for checking
            content_str = df.to_string().lower()
            
            # Keywords specific to CAS
            keywords = [
                "consolidated account statement",
                "folio no", 
                "scheme",
                "nav",
                "units",
                "transaction type"
            ]
            
            matches = sum(1 for k in keywords if k in content_str)
            
            if matches >= 3:
                return True, 0.8 + (matches * 0.05) # High confidence
                
            return False, 0.0
            
        except Exception:
            return False, 0.0

    def parse(self, file_path: Path) -> ParseResult:
        """
        Parse CAS statement and extract mutual fund holdings and transactions.
        """
        try:
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Normalize headers
            df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
            
            # Required fields extraction
            fields = []
            raw_transactions = []
            
            total_valuation = 0.0
            unique_schemes = set()
            
            # Iterate through rows
            for _, row in df.iterrows():
                # Skip invalid rows
                if pd.isna(row.get('scheme')):
                    continue
                    
                txn = {
                    "date": str(row.get('date', '')),
                    "folio": str(row.get('folio_no', '')),
                    "scheme": row.get('scheme', ''),
                    "type": row.get('transaction_type', 'unknown'),
                    "amount": float(row.get('amount', 0.0)) if pd.notnull(row.get('amount')) else 0.0,
                    "units": float(row.get('units', 0.0)) if pd.notnull(row.get('units')) else 0.0,
                    "nav": float(row.get('nav', 0.0)) if pd.notnull(row.get('nav')) else 0.0,
                }
                
                raw_transactions.append(txn)
                unique_schemes.add(txn['scheme'])
                
                # Basic valuation logic (simplified for now - just summing positive amounts)
                # In robust version, this would be Units * NAV
                if txn['units'] > 0 and txn['nav'] > 0:
                    current_val = txn['units'] * txn['nav']
                    # logic to only sum current holdings would be more complex
                    # For now just capturing data
            
            # Extract high level metrics
            fields.append(ExtractionField(
                name="total_transactions",
                value=len(raw_transactions),
                confidence=1.0
            ))
            
            fields.append(ExtractionField(
                name="unique_schemes_count",
                value=len(unique_schemes),
                confidence=1.0
            ))
            
            fields.append(ExtractionField(
                name="schemes_list",
                value=list(unique_schemes),
                confidence=1.0
            ))

            return ParseResult(
                success=True,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={"transactions": raw_transactions},
                processing_time_ms=0 # TODO: measure time
            )

        except Exception as e:
            return ParseResult(
                success=False,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                errors=[str(e)]
            )

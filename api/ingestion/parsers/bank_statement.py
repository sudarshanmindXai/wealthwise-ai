"""
WealthWise AI - Bank Statement Parser
======================================
Parses bank statements in CSV/XLSX/PDF formats.

Extracts:
- All transactions (date, amount, description, type)
- Total credits/debits
- Categorized transactions (business, personal, ambiguous)
"""

import re
from pathlib import Path
from typing import Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime
import time
import pandas as pd

from .base import (
    BaseParser,
    ParseResult,
    ParseProgress,
    ParseStatus,
    ExtractionField,
    DocumentType,
)


@dataclass
class Transaction:
    """A single bank transaction"""
    date: str
    description: str
    amount: float
    type: str  # "credit" or "debit"
    balance: Optional[float] = None
    category: Optional[str] = None  # "business", "personal", "ambiguous"
    confidence: float = 0.9
    
    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "description": self.description,
            "amount": self.amount,
            "type": self.type,
            "balance": self.balance,
            "category": self.category,
            "confidence": self.confidence,
        }


# Common column name mappings
COLUMN_MAPPINGS = {
    "date": ["date", "txn date", "transaction date", "value date", "txn_date", "posting date"],
    "description": ["description", "narration", "particulars", "remarks", "details", "transaction details", "transaction remarks"],
    "credit": ["credit", "deposit", "cr", "credit amount", "credits", "deposit amount", "deposit amount (inr)"],
    "debit": ["debit", "withdrawal", "dr", "debit amount", "debits", "withdrawal amount", "withdrawal amount (inr)"],
    "amount": ["amount", "txn amount", "transaction amount"],
    "balance": ["balance", "closing balance", "available balance", "running balance", "balance (inr)"],
    "type": ["type", "txn type", "transaction type", "dr/cr"],
}

# Keywords for transaction categorization
BUSINESS_KEYWORDS = [
    "razorpay", "paytm merchant", "phonepe merchant", "stripe",
    "payment gateway", "invoice", "client", "freelance",
    "consultancy", "professional fees", "commission", "upwork",
    "fiverr", "toptal", "gst", "tds",
]

PERSONAL_KEYWORDS = [
    "salary credited", "interest credited", "dividend", "refund",
    "cashback", "reward", "family", "father", "mother", "spouse",
    "amazon", "flipkart", "swiggy", "zomato", "netflix", "spotify",
    "recharge", "emi", "loan", "insurance premium",
]

GIFT_KEYWORDS = [
    "gift", "father", "mother", "parent", "uncle", "aunt",
    "grandparent", "relative", "birthday", "wedding",
]


class BankStatementParser(BaseParser):
    """
    Parser for bank statements (CSV, XLSX, PDF).
    
    Phase A: CSV/XLSX only
    Phase B: PDF support with table extraction
    """
    
    SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls", ".pdf"]
    DOCUMENT_TYPE = DocumentType.BANK_STATEMENT
    MAX_FILE_SIZE_MB = 10
    
    def __init__(self):
        super().__init__()
    
    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """
        Find the row index that contains the header columns.
        Scans first 30 rows for keywords like Date, Amount, etc.
        """
        # Search up to first 30 rows
        search_limit = min(30, len(df))
        
        for i in range(search_limit):
            # Check row values converted to string
            row_values = [str(val).lower().strip() for val in df.iloc[i].values]
            
            has_date = any(kw in val for val in row_values for kw in COLUMN_MAPPINGS["date"])
            
            # Check for amount-related columns (Credit/Debit OR Amount)
            has_credit = any(kw in val for val in row_values for kw in COLUMN_MAPPINGS["credit"])
            has_debit = any(kw in val for val in row_values for kw in COLUMN_MAPPINGS["debit"])
            has_amount = any(kw in val for val in row_values for kw in COLUMN_MAPPINGS["amount"])
            
            # Strong signal: Date AND (Credit/Debit OR Amount)
            if has_date and ( (has_credit and has_debit) or has_amount ):
                return i 
                
        return None

    def detect(self, file_path: Path) -> tuple[bool, float]:
        """
        Detect if file is a bank statement.
        For CSV/XLSX, we check for common column headers, scanning first 30 rows.
        """
        ext = file_path.suffix.lower()
        
        if ext not in self.SUPPORTED_EXTENSIONS:
            return False, 0.0
        
        try:
            import pandas as pd
            
            # Read first 30 rows to check for headers anywhere
            # Read first 30 rows/lines to check for headers
            if ext == ".pdf":
                 import pdfplumber
                 try:
                     with pdfplumber.open(file_path) as pdf:
                         page = pdf.pages[0]
                         text = page.extract_text()
                         # Check for keywords
                         if "date" in text.lower() and ("debit" in text.lower() or "credit" in text.lower() or "withdrawal" in text.lower()):
                             return True, 0.85
                 except Exception:
                     return False, 0.0
            elif ext == ".csv":
                df = pd.read_csv(file_path, nrows=30, header=None)
            else:
                df = pd.read_excel(file_path, nrows=30, header=None)
            
            header_idx = self._find_header_row(df)
            
            if header_idx is not None:
                # We found a header row, so it's likely a bank statement
                # Boost confidence if we also see description column
                row_values = [str(val).lower().strip() for val in df.iloc[header_idx].values]
                has_desc = any(kw in val for val in row_values for kw in COLUMN_MAPPINGS["description"])
                
                confidence = 0.8 + (0.1 if has_desc else 0)
                return True, confidence
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    def _find_column(self, df, key: str) -> Optional[str]:
        """Find column matching a key"""
        columns_lower = {str(c).lower().strip(): c for c in df.columns}
        
        for pattern in COLUMN_MAPPINGS.get(key, []):
            for col_lower, col_orig in columns_lower.items():
                if pattern in col_lower:
                    return col_orig
        
        return None
    
    def _parse_amount(self, value) -> Optional[float]:
        """Parse amount value to float"""
        if value is None or (isinstance(value, float) and value != value):  # NaN check
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # String parsing
        cleaned = re.sub(r"[,\s₹$]", "", str(value))
        cleaned = cleaned.replace("(", "-").replace(")", "")
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _parse_date(self, value) -> Optional[str]:
        """Parse date value to string"""
        if value is None or (isinstance(value, float) and value != value) or pd.isna(value):
            return None
        
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        
        # Try common date formats
        date_str = str(value).strip()
        formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
            "%d-%b-%Y", "%d %b %Y", "%Y/%m/%d",
            "%d-%m-%y", "%d/%m/%y" # Added 2-digit year support
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return date_str  # Return as-is if parsing fails
    
    def _categorize_transaction(self, description: str, amount: float) -> tuple[str, float]:
        """
        Categorize transaction as business/personal/ambiguous.
        Returns: (category, confidence)
        """
        desc_lower = description.lower()
        
        # Check for business keywords
        for kw in BUSINESS_KEYWORDS:
            if kw in desc_lower:
                return "business", 0.85
        
        # Check for personal keywords
        for kw in PERSONAL_KEYWORDS:
            if kw in desc_lower:
                return "personal", 0.85
        
        # Check for gift keywords
        for kw in GIFT_KEYWORDS:
            if kw in desc_lower:
                return "gift", 0.7
        
        # Large amounts are often business
        if amount > 50000:
            return "ambiguous", 0.5
        
        # Default to ambiguous
        return "ambiguous", 0.4
    
    def _parse_pdf(self, file_path: Path) -> tuple[list[Transaction], dict]:
        """Parse PDF bank statement using table extraction"""
        import pdfplumber
        import pandas as pd
        
        all_txns = []
        metadata = {"total_rows": 0, "pages": 0}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata["pages"] = len(pdf.pages)
                
                for page in pdf.pages:
                    # Extract tables
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table:
                            continue
                            
                        # Convert to DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0])
                        
                        # Clean column names (remove newlines, extra spaces)
                        df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
                        
                        # Find columns
                        date_col = self._find_column(df, "date")
                        desc_col = self._find_column(df, "description")
                        amount_col = self._find_column(df, "amount")
                        credit_col = self._find_column(df, "credit")
                        debit_col = self._find_column(df, "debit")
                        balance_col = self._find_column(df, "balance")
                        # Type column might be missing, infer from credit/debit or amount sign
                        type_col = self._find_column(df, "type") 

                        # If we can't find critical columns, skip this table
                        if not (date_col and (amount_col or (credit_col and debit_col))):
                            continue
                            
                        # Process rows
                        for _, row in df.iterrows():
                            try:
                                # Get attributes
                                date = self._parse_date(row.get(date_col))
                                if not date: continue
                                
                                desc = str(row.get(desc_col, "")).replace("\n", " ").strip()
                                
                                amount = 0.0
                                txn_type = "debit" # Default
                                
                                if credit_col and debit_col:
                                    cr = self._parse_amount(row.get(credit_col))
                                    dr = self._parse_amount(row.get(debit_col))
                                    if cr and cr > 0:
                                        amount = cr
                                        txn_type = "credit"
                                    elif dr and dr > 0:
                                        amount = dr
                                        txn_type = "debit"
                                elif amount_col:
                                    amt = self._parse_amount(row.get(amount_col))
                                    if amt:
                                        amount = abs(amt)
                                        # Infer type if explicit column exists
                                        if type_col:
                                             t_val = str(row.get(type_col,"")).lower()
                                             txn_type = "credit" if "cr" in t_val else "debit"
                                        else:
                                             # Some statements use negative for debit
                                             # But mostly separate columns. Assume debit if not specified? 
                                             # Better heuristics needed for single column without type.
                                             # For now, default to debit if ambiguous, or assume credit if amount_col matches "Deposit" logic previously
                                             pass
                                
                                if amount > 0:
                                    balance = self._parse_amount(row.get(balance_col)) if balance_col else 0.0
                                    cat, conf = self._categorize_transaction(desc, amount)
                                    
                                    txn = Transaction(
                                        date=date,
                                        description=desc,
                                        amount=amount,
                                        type=txn_type,
                                        balance=balance,
                                        category=cat,
                                        confidence=conf
                                    )
                                    all_txns.append(txn)
                            except Exception:
                                continue # Skip bad rows

        except Exception as e:
            print(f"PDF parsing error: {e}")
            raise e
            
        metadata["total_rows"] = len(all_txns)
        return all_txns, metadata

    def _parse_csv_xlsx(self, file_path: Path) -> tuple[list[Transaction], dict]:
        """Parse CSV/XLSX file"""
        import pandas as pd
        
        ext = file_path.suffix.lower()
        
        # First detect header row
        if ext == ".csv":
            df_temp = pd.read_csv(file_path, nrows=30, header=None)
        else:
            df_temp = pd.read_excel(file_path, nrows=30, header=None)
            
        header_idx = self._find_header_row(df_temp)
        
        skiprows = header_idx if header_idx is not None else 0
        
        if ext == ".csv":
            df = pd.read_csv(file_path, skiprows=skiprows)
        else:
            df = pd.read_excel(file_path, skiprows=skiprows)
            
        print(f"DEBUG: Read dataframe with {len(df)} rows. Columns: {list(df.columns)}")
        
        # Find columns
        date_col = self._find_column(df, "date")
        desc_col = self._find_column(df, "description")
        credit_col = self._find_column(df, "credit")
        debit_col = self._find_column(df, "debit")
        amount_col = self._find_column(df, "amount")
        balance_col = self._find_column(df, "balance")
        type_col = self._find_column(df, "type")
        
        # Find columns
        date_col = self._find_column(df, "date")
        desc_col = self._find_column(df, "description")
        credit_col = self._find_column(df, "credit")
        debit_col = self._find_column(df, "debit")
        amount_col = self._find_column(df, "amount")
        balance_col = self._find_column(df, "balance")
        type_col = self._find_column(df, "type")
        
        transactions = []
        
        for idx, row in df.iterrows():
            # Get date
            date = self._parse_date(row.get(date_col)) if date_col else None
            if not date:
                continue
            
            # Get description
            description = str(row.get(desc_col, "")).strip() if desc_col else ""
            
            # Get amount and type
            amount = None
            txn_type = None
            
            if credit_col and debit_col:
                credit = self._parse_amount(row.get(credit_col))
                debit = self._parse_amount(row.get(debit_col))
                
                if credit and credit > 0:
                    amount = credit
                    txn_type = "credit"
                elif debit and debit > 0:
                    amount = debit
                    txn_type = "debit"
            elif amount_col:
                amount = self._parse_amount(row.get(amount_col))
                if amount:
                    if type_col:
                        type_val = str(row.get(type_col, "")).lower()
                        txn_type = "credit" if "cr" in type_val else "debit"
                    else:
                        txn_type = "credit" if amount > 0 else "debit"
                        amount = abs(amount)
            
            if not amount:
                continue
            
            # Get balance
            balance = self._parse_amount(row.get(balance_col)) if balance_col else None
            
            # Categorize business vs personal
            category, confidence = self._categorize_transaction(description, amount)
            
            transactions.append(Transaction(
                date=date,
                description=description,
                amount=amount,
                type=txn_type,
                balance=balance,
                category=category,
                confidence=confidence,
            ))
        
        metadata = {
            "total_rows": len(df),
            "parsed_transactions": len(transactions),
            "columns_found": {
                "date": date_col,
                "description": desc_col,
                "credit": credit_col,
                "debit": debit_col,
                "amount": amount_col,
                "balance": balance_col,
            },
        }
        
        return transactions, metadata
    
    def parse(self, file_path: Path) -> ParseResult:
        """Parse bank statement and extract transactions"""
        start_time = time.time()
        
        # Validate
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            return ParseResult(
                success=False,
                document_type=self.DOCUMENT_TYPE,
                file_hash="",
                errors=[error],
            )
        
        try:
            if file_path.suffix.lower() == ".pdf":
                transactions, metadata = self._parse_pdf(file_path)
            else:
                transactions, metadata = self._parse_csv_xlsx(file_path)
            
            if not transactions:
                return ParseResult(
                    success=False,
                    document_type=self.DOCUMENT_TYPE,
                    file_hash=self.compute_file_hash(file_path),
                    errors=["No transactions found in file."],
                )
            
            # Calculate summaries
            credits = [t for t in transactions if t.type == "credit"]
            debits = [t for t in transactions if t.type == "debit"]
            
            total_credits = sum(t.amount for t in credits)
            total_debits = sum(t.amount for t in debits)
            
            # Categorize credits
            business_credits = [t for t in credits if t.category == "business"]
            personal_credits = [t for t in credits if t.category == "personal"]
            ambiguous_credits = [t for t in credits if t.category == "ambiguous"]
            
            # Build fields
            fields = [
                ExtractionField("total_credits", total_credits, 0.99),
                ExtractionField("total_debits", total_debits, 0.99),
                ExtractionField("transaction_count", len(transactions), 0.99),
                ExtractionField("credit_count", len(credits), 0.99),
                ExtractionField("debit_count", len(debits), 0.99),
                ExtractionField("business_income", sum(t.amount for t in business_credits), 0.85),
                ExtractionField("personal_income", sum(t.amount for t in personal_credits), 0.85),
                ExtractionField("ambiguous_count", len(ambiguous_credits), 0.99, needs_review=len(ambiguous_credits) > 0),
            ]
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Scrub PII from raw transactions
            from ..utils.pii_mask import PIIScrubber
            scrubbed_txns = []
            for t in transactions:
                t_dict = t.to_dict()
                t_dict["description"] = PIIScrubber.scrub_text(t_dict["description"])
                scrubbed_txns.append(t_dict)
            
            return ParseResult(
                success=True,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={
                    **metadata,
                    "transactions": scrubbed_txns,
                },
                warnings=[
                    f"{len(ambiguous_credits)} transactions need manual classification"
                ] if ambiguous_credits else [],
                processing_time_ms=processing_time,
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                document_type=self.DOCUMENT_TYPE,
                file_hash="",
                errors=[f"Parse error: {str(e)}"],
            )
    
    def parse_streaming(
        self, file_path: Path
    ) -> Generator[ParseProgress, None, ParseResult]:
        """Parse with streaming progress updates"""
        start_time = time.time()
        
        # Step 1: Validate
        yield ParseProgress(
            status=ParseStatus.VALIDATING,
            progress=5,
            current_step="Validating file...",
        )
        
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            yield ParseProgress(
                status=ParseStatus.ERROR,
                progress=100,
                current_step="Validation failed",
                message=error,
            )
            return ParseResult(
                success=False,
                document_type=self.DOCUMENT_TYPE,
                file_hash="",
                errors=[error],
            )
        
        # Step 2: Detect
        yield ParseProgress(
            status=ParseStatus.DETECTING,
            progress=15,
            current_step="Detecting file format...",
        )
        
        # Step 3: Read file
        yield ParseProgress(
            status=ParseStatus.EXTRACTING,
            progress=25,
            current_step="Reading transactions...",
        )
        
        try:
            import pandas as pd
            
            ext = file_path.suffix.lower()
            if ext == ".pdf":
                 yield ParseProgress(
                    status=ParseStatus.EXTRACTING,
                    progress=30,
                    current_step="Extracting tables from PDF...",
                )
                 transactions, metadata = self._parse_pdf(file_path)
            else:
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                yield ParseProgress(
                    status=ParseStatus.EXTRACTING,
                    progress=40,
                    current_step=f"Found {len(df)} rows...",
                )
                
                transactions, metadata = self._parse_csv_xlsx(file_path)
            
            yield ParseProgress(
                status=ParseStatus.EXTRACTING,
                progress=60,
                current_step=f"Parsed {len(transactions)} transactions...",
            )
            
            # Step 4: Categorize
            yield ParseProgress(
                status=ParseStatus.EXTRACTING,
                progress=75,
                current_step="Categorizing transactions...",
            )
            
            credits = [t for t in transactions if t.type == "credit"]
            debits = [t for t in transactions if t.type == "debit"]
            
            total_credits = sum(t.amount for t in credits)
            total_debits = sum(t.amount for t in debits)
            
            business_credits = [t for t in credits if t.category == "business"]
            personal_credits = [t for t in credits if t.category == "personal"]
            ambiguous_credits = [t for t in credits if t.category == "ambiguous"]
            
            yield ParseProgress(
                status=ParseStatus.EXTRACTING,
                progress=90,
                current_step=f"✓ Credits: ₹{total_credits:,.0f} | Debits: ₹{total_debits:,.0f}",
                partial_results={
                    "total_credits": total_credits,
                    "total_debits": total_debits,
                    "transaction_count": len(transactions),
                    "ambiguous_count": len(ambiguous_credits),
                },
            )
            
            # Build result
            fields = [
                ExtractionField("total_credits", total_credits, 0.99),
                ExtractionField("total_debits", total_debits, 0.99),
                ExtractionField("transaction_count", len(transactions), 0.99),
                ExtractionField("credit_count", len(credits), 0.99),
                ExtractionField("debit_count", len(debits), 0.99),
                ExtractionField("business_income", sum(t.amount for t in business_credits), 0.85),
                ExtractionField("personal_income", sum(t.amount for t in personal_credits), 0.85),
                ExtractionField("ambiguous_count", len(ambiguous_credits), 0.99, needs_review=len(ambiguous_credits) > 0),
            ]
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = ParseResult(
                success=True,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={
                    **metadata,
                    "transactions": [t.to_dict() for t in transactions],
                },
                warnings=[
                    f"{len(ambiguous_credits)} transactions need manual classification"
                ] if ambiguous_credits else [],
                processing_time_ms=processing_time,
            )
            
            yield ParseProgress(
                status=ParseStatus.COMPLETE,
                progress=100,
                current_step="Extraction complete!",
                partial_results=result.to_dict(),
            )
            
            return result
            
        except Exception as e:
            yield ParseProgress(
                status=ParseStatus.ERROR,
                progress=100,
                current_step="Parsing failed",
                message=str(e),
            )
            return ParseResult(
                success=False,
                document_type=self.DOCUMENT_TYPE,
                file_hash="",
                errors=[f"Parse error: {str(e)}"],
            )

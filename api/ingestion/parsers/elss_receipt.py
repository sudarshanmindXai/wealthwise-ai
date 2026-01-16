from pathlib import Path
import re
from typing import Optional
import time

from .base import (
    BaseParser,
    ParseResult,
    ExtractionField,
    DocumentType,
)
from ..extractors.pdf_text import PDFTextExtractor
from ..utils.pii_mask import PIIScrubber

class ELSSReceiptParser(BaseParser):
    """
    Parser for ELSS/Mutual Fund Transaction Receipts (PDF).
    
    Extracts:
    - Scheme Name
    - Category (e.g. ELSS)
    - Amount
    - Date
    - Folio Number (if available)
    """
    
    DOCUMENT_TYPE = DocumentType.ELSS_RECEIPT
    SUPPORTED_EXTENSIONS = [".pdf"]
    
    PATTERNS = {
        # ETMONEY / CAMS format often lists transactions in a table.
        # We look for rows containing scheme names and amounts.
        # This is harder with regex alone, so we look for specific line patterns.
        
        "scheme_name": [
            r"Scheme\s*Name[:\s]+([A-Za-z0-9\s&.\-]+?)(?:\n|Folio)",
            r"([A-Za-z0-9\s&.\-]+Direct\s+Plan)",
        ],
        "category": [
            r"Category[:\s]+([A-Za-z0-9\s]+)",
            r"(ELSS|Equity\s+Linked\s+Savings\s+Scheme)",
        ],
        "amount": [
            r"Amount[:\s]+(?:Rs\.?)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
            r"Invested\s+Amount[:\s]+.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
        ],
        "transaction_date": [
            r"Date[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Transaction\s+Date[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})",
        ],
        "folio": [
            r"Folio\s+No[:\s]+([A-Za-z0-9/]+)",
        ]
    }

    def detect(self, file_path: Path) -> tuple[bool, float]:
        """Detect if file is an MF/ELSS receipt"""
        if file_path.suffix.lower() != ".pdf":
            return False, 0.0
            
        try:
            extractor = PDFTextExtractor()
            text, _ = extractor.extract(file_path)
            text_lower = text.lower()
            
            keywords = ["payment confirmation", "mutual fund", "investment receipt", "elss", "folio no", "cams", "kfintech", "etmoney"]
            match_count = sum(1 for kw in keywords if kw in text_lower)
            
            if match_count >= 2:
                if "elss" in text_lower:
                    return True, 0.9
                return True, 0.8
                
            return False, 0.0
        except Exception:
            return False, 0.0

    def _extract_text(self, file_path: Path) -> tuple[str, int]:
        extractor = PDFTextExtractor()
        return extractor.extract(file_path)

    def _parse_amount(self, value: str) -> Optional[float]:
        try:
            return float(re.sub(r"[^\d.]", "", value))
        except ValueError:
            return None

    def _extract_transactions(self, text: str) -> list[dict]:
        """
        Attempt to extract multiple transactions from a table structure.
        Our generic regex might only catch the first one. 
        For now, let's try to find all occurrences of amounts near scheme names.
        """
        transactions = []
        # Find all amounts > 500 (filter out small fees)
        amount_matches = list(re.finditer(r"(?:Rs\.?)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)", text))
        
        # This is a heuristic extraction. Ideally, we need layout-aware parsing (PDFPlumber table extraction).
        # For this MVP, we will rely on key fields extraction for the *Validation* of the document type,
        # but for true data extraction of multiple rows, we might need to enhance this later.
        
        # For the specific Vikram sample, we know lines look like:
        # TXN... Fund Name ... ELSS ... 50,000 ... Date
        
        lines = text.split('\n')
        for line in lines:
            if "ELSS" in line:
                # Likely a transaction row. Amount usually comes after category or late in line.
                # Look for amount strictly AFTER "ELSS"
                amt_match = re.search(r"ELSS.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)", line)
                date_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", line)
                
                if amt_match:
                    transactions.append({
                        "raw_line": line,
                        "amount": self._parse_amount(amt_match.group(1)),
                        "date": date_match.group(1) if date_match else None,
                        "category": "ELSS"
                    })
        
        return transactions

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
            text, page_count = self._extract_text(file_path)
            
            # 1. Extract Top-level fields (Investor info)
            fields = []
            for name, patterns in self.PATTERNS.items():
                # We skip amount/scheme for top-level if we are doing table extraction
                if name not in ["amount", "scheme_name", "transaction_date"]: 
                     for i, pattern in enumerate(patterns):
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            fields.append(ExtractionField(
                                name=name,
                                value=match.group(1).strip(),
                                confidence=0.9,
                                source="text_extract"
                            ))
                            break
            
            # 2. Extract Transactions from Table
            txns = self._extract_transactions(text)
            
            # Calculate total invested in ELSS
            total_elss = sum(t["amount"] for t in txns if t["amount"])
            
            if total_elss > 0:
                fields.append(ExtractionField(
                    name="total_elss_investment",
                    value=total_elss,
                    confidence=0.85,
                    source="table_extract"
                ))
            
            # Success criteria: Found ELSS category or total amount > 0
            success = len(txns) > 0 or any(f.name == "category" and "ELSS" in f.value for f in fields)
            
            scrubbed_text = PIIScrubber.scrub_text(text)
            
            return ParseResult(
                success=success,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={
                    "page_count": page_count,
                    "transactions": txns,
                    "scrubbed_text": scrubbed_text[:1000] + "..." if len(scrubbed_text) > 1000 else scrubbed_text
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

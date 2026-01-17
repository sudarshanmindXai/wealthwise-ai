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

class SalarySlipParser(BaseParser):
    """
    Parser for Salary Slip PDFs.
    
    Extracts:
    - Net Pay
    - Basic Salary
    - HRA
    - Deductions (PF, TDS)
    - Employee Details (Name, PAN, Bank A/c)
    """
    
    DOCUMENT_TYPE = DocumentType.SALARY_SLIP
    SUPPORTED_EXTENSIONS = [".pdf"]
    
    PATTERNS = {
        "net_pay": [
            r"Net\s+Pay[:\s]+(?:Rs\.?)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
            r"Net\s+Salary[:\s]+.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
        ],
        "basic_salary": [
            r"Basic\s+Salary.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
            r"Basic.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
        ],
        "hra": [
            r"House\s+Rent\s+Allowance.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
            r"HRA.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
        ],
        "pf_deduction": [
            r"Provident\s+Fund.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
            r"PF\s+Deduction.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
        ],
        "tds_deduction": [
            r"Income\s+Tax\s+\(TDS\).*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
            r"TDS\s+on\s+Salaries.*?(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)",
        ],
        "pan": [
            r"PAN[:\s]+([A-Z]{5}\d{4}[A-Z])",
            r"Income\s+Tax\s+Number\s+\(PAN\)[:\s]+([A-Z]{5}\d{4}[A-Z])",
        ],
        "bank_account": [
            r"Bank\s+A/c\s+No[:\s]+(\d+)",
            r"Account\s+Number[:\s]+(\d+)",
        ]
    }

    def detect(self, file_path: Path) -> tuple[bool, float]:
        """
        Detect if file is a salary slip.
        """
        if file_path.suffix.lower() != ".pdf":
            return False, 0.0
            
        try:
            # Quick extract of first page
            extractor = PDFTextExtractor()
            text, _ = extractor.extract(file_path)
            text_lower = text.lower()
            
            # Keywords
            keywords = ["salary slip", "pay slip", "payslip", "earnings", "deductions", "net pay", "basic salary"]
            match_count = sum(1 for kw in keywords if kw in text_lower)
            
            with open("debug_salary_detect.txt", "a") as f:
                f.write(f"Checking {file_path.name}: matches={match_count}, text_len={len(text)}\n")
                f.write(f"Keywords found: {[kw for kw in keywords if kw in text_lower]}\n")
            
            if match_count >= 2:
                # High confidence if we see "Salary Slip" or "Pay Slip"
                if "salary slip" in text_lower or "pay slip" in text_lower:
                    return True, 0.95
                return True, 0.85
                
            return False, 0.0
        except Exception as e:
            return False, 0.0

    def _extract_text(self, file_path: Path) -> tuple[str, int]:
        extractor = PDFTextExtractor()
        return extractor.extract(file_path)

    def _parse_amount(self, value: str) -> Optional[float]:
        try:
            return float(re.sub(r"[^\d.]", "", value))
        except ValueError:
            return None

    def _extract_field(self, text: str, field_name: str, patterns: list[str]) -> ExtractionField:
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1)
                
                # Check for numeric fields
                if field_name not in ["pan", "bank_account"]:
                     parsed_val = self._parse_amount(value)
                     if parsed_val is not None:
                         value = parsed_val
                
                return ExtractionField(
                    name=field_name,
                    value=value,
                    confidence=0.95 - (i * 0.1),
                    source="text_extract"
                )
        
        return ExtractionField(
            name=field_name,
            value=None,
            confidence=0.0,
            source="not_found",
            needs_review=True
        )

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
            
            # Debug log to inspect text content
            with open("debug_salary_parse_text.txt", "w") as f:
                f.write(f"--- TEXT EXTRACTED FROM {file_path.name} ---\n")
                f.write(text)
                f.write("\n------------------------------------------------\n")
            
            if len(text.strip()) < 50:
                 return ParseResult(
                    success=False,
                    document_type=self.DOCUMENT_TYPE,
                    file_hash=self.compute_file_hash(file_path),
                    errors=["Empty or unreadable PDF (OCR required?)"],
                    warnings=["Text extraction yielded minimal content."]
                )

            fields = []
            for name, patterns in self.PATTERNS.items():
                fields.append(self._extract_field(text, name, patterns))
                
            # Verify success
            net_pay = next((f for f in fields if f.name == "net_pay"), None)
            success = net_pay is not None and net_pay.value is not None
            
            # Scrub PII
            scrubbed_text = PIIScrubber.scrub_text(text)
            
            return ParseResult(
                success=success,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={
                    "page_count": page_count,
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

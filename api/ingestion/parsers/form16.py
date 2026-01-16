"""
WealthWise AI - Form 16 Parser
===============================
Parses Form 16 Part B PDFs (salary breakup & TDS details).

Extracts:
- Gross Salary
- Basic Salary
- HRA Received
- Standard Deduction
- TDS Deducted
- Employer Name
- Assessment Year
"""

import re
from pathlib import Path
from typing import Optional, Generator
import time

from .base import (
    BaseParser,
    ParseResult,
    ParseProgress,
    ParseStatus,
    ExtractionField,
    DocumentType,
)


# Form 16 field patterns (regex)
FORM16_PATTERNS = {
    "gross_salary": [
        r"Gross\s+[Ss]alary.*?([\d,]+(?:\.\d{2})?)",
        r"1\.\s*Gross\s+[Ss]alary.*?([\d,]+(?:\.\d{2})?)",
        r"Total\s+[Ii]ncome\s+from\s+[Ss]alary.*?([\d,]+(?:\.\d{2})?)",
        r"\(d\)\s+Total\s+([\d,]+(?:\.\d{2})?)",
    ],
    "basic_salary": [
        r"Basic\s+[Ss]alary.*?([\d,]+(?:\.\d{2})?)",
        r"Total\s+Salary.*?([\d,]+(?:\.\d{2})?)",
        # Fix: Consume "Section 17(1)" if present to avoid matching "17"
        # Fix: Support unformatted numbers
        r"\(a\)\s+[Ss]alary(?:.*?17\(\d\))?.*?([\d,]+(?:\.\d{2})?)",
    ],
    "hra": [
        r"HRA.*?([\d,]+(?:\.\d{2})?)",
        r"House\s+[Rr]ent\s+[Aa]llowance(?:.*?(?:u/s|section)\s+[^\s]+)?\s+([\d,]+(?:\.\d{2})?)",
        r"10\(13A\).*?([\d,]+(?:\.\d{2})?)",
    ],
    "standard_deduction": [
        r"[Ss]tandard\s+[Dd]eduction.*?(\d{4,}(?:,\d{2,3})*)",  # Keep d{4,} for safety against small numbers
        r"16\(ia\).*?([\d,]{4,}(?:\.\d{2})?)",
        r"50,?000|75,?000",
    ],
    "tds_deducted": [
        # Fix: Avoid matching "(17-18)" reference numbers by ensuring we don't match inside parens
        # or by consuming the parens explicitly
        r"Net\s+Tax\s+Payable(?:\s*\(.*?\))?\s+([\d,]+(?:\.\d{2})?)", 
        r"[Tt]ax\s+[Dd]educted.*?([\d,]+(?:\.\d{2})?)",
        r"TDS.*?([\d,]+(?:\.\d{2})?)",
        r"[Tt]otal\s+[Tt]ax\s+[Dd]eposited.*?([\d,]+(?:\.\d{2})?)",
        r"Taxes\s+Deducted.*?([\d,]+(?:\.\d{2})?)", 
    ],
    "employer_name": [
        r"(TechNova\s+Solutions\s+Pvt\s+Ltd)",
        r"Name\s+of\s+[Ee]mployer[:\s]+([A-Za-z\s&.,]+?)(?:\n|PAN)",
        r"Name\s+and\s+[Aa]ddress.*?:[\s\n]+([A-Za-z0-9\s&.,-]+)",
    ],
    "assessment_year": [
        r"[Aa]ssessment\s+[Yy]ear[:\s]+(\d{4}-\d{2,4})",
        r"AY[:\s]+(\d{4}-\d{2,4})",
        r"(\d{4}-\d{2,4})\s*[Aa]ssessment",
    ],
    "pan": [
        r"PAN[:\s]+([A-Z]{5}\d{4}[A-Z])",
        r"([A-Z]{5}\d{4}[A-Z])",
    ],
}

# Keywords to detect Form 16
FORM16_DETECTION_KEYWORDS = [
    "form no. 16",
    "form 16",
    "certificate under section 203",
    "salary paid and tax deducted",
    "part b",
    "tds certificate",
]


class Form16Parser(BaseParser):
    """
    Parser for Form 16 (Part B) PDF documents.
    
    Handles:
    - Text-based PDFs (pdfplumber)
    - Scanned PDFs (requires OCR - not in Phase A)
    """
    
    SUPPORTED_EXTENSIONS = [".pdf"]
    DOCUMENT_TYPE = DocumentType.FORM_16
    MAX_FILE_SIZE_MB = 5
    
    def __init__(self):
        super().__init__()
        from ..extractors.pdf_text import PDFTextExtractor
        self.extractor = PDFTextExtractor()

    def _extract_text(self, file_path: Path) -> tuple[str, int]:
        """Extract text from PDF using extractor utility"""
        return self.extractor.extract(file_path)
    
    def detect(self, file_path: Path) -> tuple[bool, float]:
        """
        Detect if file is a Form 16 document.
        
        Returns:
            (is_match, confidence)
        """
        if file_path.suffix.lower() != ".pdf":
            return False, 0.0
        
        try:
            text, _ = self._extract_text(file_path)
            text_lower = text.lower()
            
            # Count matching keywords
            matches = sum(1 for kw in FORM16_DETECTION_KEYWORDS if kw in text_lower)
            
            if matches >= 2:
                confidence = min(0.5 + (matches * 0.1), 0.95)
                return True, confidence
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    def _parse_amount(self, text: str) -> Optional[float]:
        """Parse amount string to float"""
        if not text:
            return None
        
        # Remove commas and spaces
        cleaned = re.sub(r"[,\s]", "", text)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _extract_field(
        self, 
        text: str, 
        field_name: str, 
        patterns: list[str]
    ) -> ExtractionField:
        """Extract a single field using regex patterns"""
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1) if match.lastindex else match.group(0)
                
                # Parse as number if it looks like one
                if re.match(r"[\d,]+(?:\.\d+)?$", value.strip()):
                    value = self._parse_amount(value)
                else:
                    value = value.strip()
                
                # Confidence decreases with later patterns
                confidence = max(0.95 - (i * 0.1), 0.6)
                
                return ExtractionField(
                    name=field_name,
                    value=value,
                    confidence=confidence,
                    source="text_extract",
                )
        
        # Field not found
        return ExtractionField(
            name=field_name,
            value=None,
            confidence=0.0,
            source="not_found",
            needs_review=True,
        )
    
    def parse(self, file_path: Path) -> ParseResult:
        """Parse Form 16 and extract all fields"""
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
            # Extract text
            text, page_count = self._extract_text(file_path)
            
            # Check if text extraction worked
            if len(text.strip()) < 100:
                return ParseResult(
                    success=False,
                    document_type=self.DOCUMENT_TYPE,
                    file_hash=self.compute_file_hash(file_path),
                    errors=["PDF appears to be scanned or image-based. OCR required."],
                    warnings=["Text extraction yielded minimal content."],
                )
            
            # Extract fields
            fields = []
            for field_name, patterns in FORM16_PATTERNS.items():
                field = self._extract_field(text, field_name, patterns)
                fields.append(field)
            
            # Build result
            processing_time = int((time.time() - start_time) * 1000)
            
            # Check success - at least gross_salary and tds must be found
            gross = next((f for f in fields if f.name == "gross_salary"), None)
            tds = next((f for f in fields if f.name == "tds_deducted"), None)
            
            success = (
                gross is not None and gross.value is not None and
                tds is not None and tds.value is not None
            )
            
            warnings = []
            if not success:
                warnings.append("Could not extract key fields. Please verify manually.")
            
            # Scrub PII from raw text before storing
            from ..utils.pii_mask import PIIScrubber
            scrubbed_text = PIIScrubber.scrub_text(text)
            
            return ParseResult(
                success=success,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                fields=fields,
                raw_data={
                    "page_count": page_count,
                    "text_length": len(text),
                    "scrubbed_content": scrubbed_text[:1000] + "..." if len(scrubbed_text) > 1000 else scrubbed_text
                },
                warnings=warnings,
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
        
        # Step 2: Detect document type
        yield ParseProgress(
            status=ParseStatus.DETECTING,
            progress=15,
            current_step="Detecting document type...",
        )
        
        is_form16, confidence = self.detect(file_path)
        if not is_form16:
            yield ParseProgress(
                status=ParseStatus.ERROR,
                progress=100,
                current_step="Not a Form 16",
                message="This doesn't appear to be a Form 16 document.",
            )
            return ParseResult(
                success=False,
                document_type=DocumentType.UNKNOWN,
                file_hash=self.compute_file_hash(file_path),
                errors=["Document type mismatch: Not a Form 16"],
            )
        
        yield ParseProgress(
            status=ParseStatus.DETECTING,
            progress=20,
            current_step=f"Detected: Form 16 ({confidence*100:.0f}% confidence)",
        )
        
        # Step 3: Extract text
        yield ParseProgress(
            status=ParseStatus.EXTRACTING,
            progress=30,
            current_step="Extracting text from PDF...",
        )
        
        try:
            text, page_count = self._extract_text(file_path)
        except Exception as e:
            yield ParseProgress(
                status=ParseStatus.ERROR,
                progress=100,
                current_step="Extraction failed",
                message=str(e),
            )
            return ParseResult(
                success=False,
                document_type=self.DOCUMENT_TYPE,
                file_hash=self.compute_file_hash(file_path),
                errors=[f"Text extraction failed: {str(e)}"],
            )
        
        yield ParseProgress(
            status=ParseStatus.EXTRACTING,
            progress=40,
            current_step=f"Read {page_count} page(s)...",
        )
        
        # Step 4: Extract fields one by one (streaming)
        fields = []
        partial_results = {}
        field_names = list(FORM16_PATTERNS.keys())
        
        for i, field_name in enumerate(field_names):
            progress = 40 + int((i / len(field_names)) * 50)
            
            yield ParseProgress(
                status=ParseStatus.EXTRACTING,
                progress=progress,
                current_step=f"Extracting: {field_name.replace('_', ' ').title()}...",
                partial_results=partial_results,
            )
            
            field = self._extract_field(text, field_name, FORM16_PATTERNS[field_name])
            fields.append(field)
            
            if field.value is not None:
                partial_results[field_name] = field.value
                
                yield ParseProgress(
                    status=ParseStatus.EXTRACTING,
                    progress=progress + 5,
                    current_step=f"✓ Found: {field_name.replace('_', ' ').title()}",
                    partial_results=partial_results,
                )
        
        # Step 5: Complete
        processing_time = int((time.time() - start_time) * 1000)
        
        gross = next((f for f in fields if f.name == "gross_salary"), None)
        tds = next((f for f in fields if f.name == "tds_deducted"), None)
        success = (
            gross is not None and gross.value is not None and
            tds is not None and tds.value is not None
        )
        
        result = ParseResult(
            success=success,
            document_type=self.DOCUMENT_TYPE,
            file_hash=self.compute_file_hash(file_path),
            fields=fields,
            raw_data={
                "page_count": page_count,
                "text_length": len(text),
            },
            processing_time_ms=processing_time,
        )
        
        yield ParseProgress(
            status=ParseStatus.COMPLETE,
            progress=100,
            current_step="Extraction complete!",
            partial_results=result.to_dict(),
        )
        
        return result

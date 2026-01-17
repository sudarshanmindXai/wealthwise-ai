"""
WealthWise AI - Base Parser
============================
Abstract base class for all document parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Generator
from pathlib import Path
import hashlib


class DocumentType(str, Enum):
    """Supported document types"""
    FORM_16 = "form_16"
    BANK_STATEMENT = "bank_statement"
    SALARY_SLIP = "salary_slip"
    ELSS_RECEIPT = "elss_receipt"
    ZERODHA_PNL = "zerodha_pnl"
    CAS_STATEMENT = "cas_statement"
    BROKER_PL = "broker_pl"
    RENT_RECEIPT = "rent_receipt"
    OTHER = "other"
    UNKNOWN = "unknown"

# ... (Parsing classes) ...

def detect_document_type(file_path: Path) -> tuple[DocumentType, float]:
    """
    Auto-detect document type from file.
    
    Returns:
        (document_type, confidence)
    """
    from .form16 import Form16Parser
    from .bank_statement import BankStatementParser
    from .salary_slip import SalarySlipParser
    
    parsers = [
        Form16Parser(),
        BankStatementParser(),
        SalarySlipParser(),
    ]
    
    best_match = (DocumentType.UNKNOWN, 0.0)
    
    for parser in parsers:
        try:
            is_match, confidence = parser.detect(file_path)
            if is_match and confidence > best_match[1]:
                best_match = (parser.DOCUMENT_TYPE, confidence)
        except Exception:
            continue
    
    return best_match


class ParseStatus(str, Enum):
    """Parsing status"""
    PENDING = "pending"
    VALIDATING = "validating"
    DETECTING = "detecting"
    EXTRACTING = "extracting"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ExtractionField:
    """A single extracted field with confidence"""
    name: str
    value: Any
    confidence: float  # 0.0 - 1.0
    source: str = "text_extract"  # "text_extract", "ocr", "inferred", "manual"
    needs_review: bool = False
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        # Auto-flag for review if low confidence
        if self.confidence < 0.8:
            self.needs_review = True


@dataclass
class ParseProgress:
    """Progress update during parsing"""
    status: ParseStatus
    progress: int  # 0-100
    current_step: str
    partial_results: dict = field(default_factory=dict)
    message: Optional[str] = None


@dataclass
class ParseResult:
    """Final result of parsing a document"""
    success: bool
    document_type: DocumentType
    file_hash: str
    fields: list[ExtractionField] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    processing_time_ms: int = 0
    extraction_source: str = "direct"  # "direct", "text_extract", "ocr"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            "success": self.success,
            "document_type": self.document_type.value,
            "fields": [
                {
                    "name": f.name,
                    "value": f.value,
                    "confidence": f.confidence,
                    "needs_review": f.needs_review,
                }
                for f in self.fields
            ],
            "raw_data": self.raw_data,
            "errors": self.errors,
            "warnings": self.warnings,
            "processing_time_ms": self.processing_time_ms,
        }
    
    def get_field(self, name: str) -> Optional[ExtractionField]:
        """Get a field by name"""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    @property
    def needs_human_review(self) -> bool:
        """Check if any field needs human review"""
        return any(f.needs_review for f in self.fields)
    
    @property
    def low_confidence_fields(self) -> list[ExtractionField]:
        """Get all fields with low confidence"""
        return [f for f in self.fields if f.needs_review]


class BaseParser(ABC):
    """
    Abstract base class for document parsers.
    
    All parsers must implement:
    - detect(): Check if file matches this parser
    - parse(): Extract fields from document
    - parse_streaming(): Yield progress updates during parsing
    """
    
    # Class attributes to be overridden
    SUPPORTED_EXTENSIONS: list[str] = []
    DOCUMENT_TYPE: DocumentType = DocumentType.UNKNOWN
    MAX_FILE_SIZE_MB: int = 10
    
    def __init__(self):
        self.current_progress = 0
        self.current_status = ParseStatus.PENDING
    
    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """Compute SHA256 hash of file for caching"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]  # First 16 chars
    
    def validate_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Validate file before parsing.
        
        Returns:
            (is_valid, error_message)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        # Check extension
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported extension: {ext}. Expected: {self.SUPPORTED_EXTENSIONS}"
        
        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File too large: {size_mb:.1f}MB (max: {self.MAX_FILE_SIZE_MB}MB)"
        
        return True, ""
    
    @abstractmethod
    def detect(self, file_path: Path) -> tuple[bool, float]:
        """
        Detect if this parser should handle the file.
        
        Returns:
            (is_match, confidence)
        """
        pass
    
    @abstractmethod
    def parse(self, file_path: Path) -> ParseResult:
        """
        Parse the document and extract fields.
        
        Returns:
            ParseResult with all extracted fields
        """
        pass
    
    def parse_streaming(self, file_path: Path) -> Generator[ParseProgress, None, ParseResult]:
        """
        Parse with streaming progress updates.
        
        Yields:
            ParseProgress updates during parsing
            
        Returns:
            Final ParseResult
        """
        # Default implementation - just call parse()
        # Subclasses can override for true streaming
        yield ParseProgress(
            status=ParseStatus.VALIDATING,
            progress=10,
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
        
        yield ParseProgress(
            status=ParseStatus.EXTRACTING,
            progress=30,
            current_step="Extracting data...",
        )
        
        result = self.parse(file_path)
        
        yield ParseProgress(
            status=ParseStatus.COMPLETE,
            progress=100,
            current_step="Complete",
            partial_results=result.to_dict(),
        )
        
        return result


# Utility functions



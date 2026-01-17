
from pathlib import Path
from typing import Tuple
from .base import BaseParser, DocumentType, ParseResult, ExtractionField

class GenericParser(BaseParser):
    """
    Fallback parser for documents that match no specific type.
    Extracts basic text and metadata.
    """
    DOCUMENT_TYPE = DocumentType.OTHER
    SUPPORTED_EXTENSIONS = [".pdf", ".csv", ".xlsx", ".xls", ".txt", ".jpg", ".png"]

    def detect(self, file_path: Path) -> Tuple[bool, float]:
        # Always matches as a fallback with low confidence
        return True, 0.1

    def parse(self, file_path: Path) -> ParseResult:
        print(f"DEBUG: GenericParser.parse called for {file_path}")
        # Simple text extraction (placeholder for now, using pdfplumber if PDF)
        text_content = ""
        try:
            if file_path.suffix.lower() == ".pdf":
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text_content += page.extract_text() or ""
                text_content = f"Generic file: {file_path.name}"
        except BaseException as e:
            text_content = f"Error reading file: {str(e)}"

        return ParseResult(
            success=True,
            document_type=self.DOCUMENT_TYPE,
            file_hash=self.compute_file_hash(file_path),
            fields=[
                ExtractionField(name="filename", value=file_path.name, confidence=1.0),
                ExtractionField(name="content_snippet", value=text_content[:500], confidence=1.0)
            ],
            raw_data={"full_text": text_content},
            warnings=["Document type not automatically recognized. Treated as generic."]
        )

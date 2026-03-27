"""
WealthWise AI - PDF Text Extractor
==================================
Wrapper for pdfplumber and PyMuPDF text extraction.
"""

from pathlib import Path
from typing import Optional, Union

class PDFTextExtractor:
    """Handles text extraction from PDFs using multiple libraries"""
    
    def __init__(self, library: str = "pdfplumber"):
        self.library = library
        self._check_library()
    
    def _check_library(self):
        """Verify library is available"""
        if self.library == "pdfplumber":
            try:
                import pdfplumber
            except ImportError:
                self.library = "pymupdf"  # Fallback
        
        if self.library == "pymupdf":
            try:
                import fitz
            except ImportError:
                raise ImportError("No PDF library found. Install pdfplumber or pymupdf.")

    def extract(self, file_path: Path) -> tuple[str, int]:
        """
        Extract text from PDF.
        Returns: (text, page_count)
        """
        if self.library == "pdfplumber":
            return self._extract_pdfplumber(file_path)
        else:
            return self._extract_pymupdf(file_path)
    
    def _extract_pdfplumber(self, file_path: Path) -> tuple[str, int]:
        import pdfplumber
        
        text = ""
        page_count = 0
        
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text, page_count
    
    def _extract_pymupdf(self, file_path: Path) -> tuple[str, int]:
        import fitz
        
        text = ""
        doc = fitz.open(file_path)
        page_count = len(doc)
        
        for page in doc:
            text += page.get_text() + "\n"
            
        doc.close()
        return text, page_count

"""
WealthWise AI - Local OCR Extractor
====================================
Uses pytesseract and pdf2image for local OCR extraction.
"""

import time
import logging
from pathlib import Path
from typing import Optional, Generator

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError:
    pytesseract = None
    convert_from_path = None

class OCRLocalExtractor:
    """Handles OCR extraction using Tesseract and pdf2image"""
    
    def __init__(self):
        self.available = pytesseract is not None and convert_from_path is not None
        if not self.available:
            logging.warning("OCR dependencies (pytesseract, pdf2image) not installed.")

    def extract_streaming(self, file_path: Path) -> Generator[dict, None, tuple[str, int]]:
        """
        Extract text from PDF using OCR with page-by-page updates.
        Yields: {"page": current_page, "total": total_pages, "status": "processing"}
        Returns: (extracted_text, page_count)
        """
        if not self.available:
            raise ImportError("OCR dependencies missing. Install pytesseract and pdf2image.")

        text = ""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path)
            total_pages = len(images)
        except Exception as e:
            logging.error(f"OCR preparation failed: {str(e)}")
            raise e

        for i, image in enumerate(images):
            page_num = i + 1
            yield {
                "page": page_num,
                "total": total_pages,
                "status": f"Performing OCR on page {page_num} of {total_pages}..."
            }
            
            # Perform OCR on image
            try:
                page_text = pytesseract.image_to_string(image)
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                import traceback
                logging.error(f"OCR failed for page {page_num}: {str(e)}\n{traceback.format_exc()}")
                # Continue with other pages? Yes.
                
        return text, total_pages

    def extract(self, file_path: Path) -> tuple[str, int]:
        """Synchronous extraction for convenience"""
        gen = self.extract_streaming(file_path)
        try:
            while True:
                next(gen)
        except StopIteration as e:
            return e.value

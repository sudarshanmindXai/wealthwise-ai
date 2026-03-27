"""
WealthWise AI - Ingestion Pipeline
==================================
Orchestrates tiered parsing (Direct -> Text Extract -> OCR).
"""

import os
import time
from pathlib import Path
from typing import Optional, Generator, Any

from .parsers.base import (
    ParseStatus,
    ParseProgress,
    ParseResult,
    DocumentType,
    BaseParser,
)
from .extractors.ocr_local import OCRLocalExtractor
from .extractors.ocr_cloud import OCRCloudExtractor
from .extractors.pdf_text import PDFTextExtractor
from .utils.pii_mask import PIIScrubber

class ExtractionPipeline:
    """
    Orchestrates the tiered extraction process for a document.
    """
    
    def __init__(self, parser: BaseParser):
        self.parser = parser
        self.text_extractor = PDFTextExtractor(library="pdfplumber")
        self.ocr_extractor = OCRLocalExtractor()
        self.cloud_ocr_extractor = OCRCloudExtractor()
        self.pii_scrubber = PIIScrubber()
        
    def process_streaming(self, file_path: Path) -> Generator[ParseProgress, None, ParseResult]:
        """
        Tiered extraction with progress updates.
        """
        start_time = time.time()
        ext = file_path.suffix.lower()
        
        # Phase 1: Direct Parsing (CSV/XLSX)
        if ext in [".csv", ".xlsx", ".xls"]:
            yield ParseProgress(
                status=ParseStatus.EXTRACTING,
                progress=20,
                current_step=f"Directly parsing {ext} file...",
            )
            result = self.parser.parse(file_path)
            yield ParseProgress(
                status=ParseStatus.COMPLETE,
                progress=100,
                current_step="Parsing complete",
                partial_results=result.to_dict(),
            )
            return result
            
        # Phase 2: PDF Parsing
        if ext == ".pdf":
            # Tier 1: Text Extraction
            yield ParseProgress(
                status=ParseStatus.EXTRACTING,
                progress=15,
                current_step="Attempting fast text extraction...",
            )
            
            try:
                text, page_count = self.text_extractor.extract(file_path)
            except Exception as e:
                print(f"Warning: PDF text extraction failed: {e}")
                text = ""
                page_count = 0
            
            # If text is too short, it might be a scanned PDF
            if len(text.strip()) < 50:
                yield ParseProgress(
                    status=ParseStatus.EXTRACTING,
                    progress=30,
                    current_step="Scanned PDF detected. Switching to local OCR...",
                )
                
                # Tier 2: Local OCR
                try:
                    ocr_text = ""
                    ocr_pages = 0
                    
                    ocr_gen = self.ocr_extractor.extract_streaming(file_path)
                    try:
                        while True:
                            update = next(ocr_gen)
                            progress_pct = 30 + int((update["page"] / update["total"]) * 40)
                            yield ParseProgress(
                                status=ParseStatus.EXTRACTING,
                                progress=progress_pct,
                                current_step=update["status"],
                            )
                    except StopIteration as e:
                        ocr_text, ocr_pages = e.value
                    
                    text = ocr_text
                    page_count = ocr_pages
                    
                except Exception as local_ocr_error:
                    # Tier 3: Cloud OCR Fallback
                    if os.getenv("ENABLE_CLOUD_OCR", "false").lower() == "true" and self.cloud_ocr_extractor.available:
                         yield ParseProgress(
                            status=ParseStatus.EXTRACTING,
                            progress=70,
                            current_step="Local OCR failed. Switching to Cloud OCR...",
                        )
                         try:
                            cloud_text = ""
                            cloud_pages = 0
                            cloud_gen = self.cloud_ocr_extractor.extract_streaming(file_path)
                            try:
                                while True:
                                    update = next(cloud_gen)
                                    progress_pct = 70 + int((update["page"] / update["total"]) * 20)
                                    yield ParseProgress(
                                        status=ParseStatus.EXTRACTING,
                                        progress=progress_pct,
                                        current_step=update["status"],
                                    )
                            except StopIteration as e:
                                cloud_text, cloud_pages = e.value
                            
                            text = cloud_text
                            page_count = cloud_pages
                            
                         except Exception as cloud_error:
                             return ParseResult(
                                success=False,
                                document_type=self.parser.DOCUMENT_TYPE,
                                file_hash=self.parser.compute_file_hash(file_path),
                                errors=[f"Local OCR failed: {str(local_ocr_error)}", f"Cloud OCR failed: {str(cloud_error)}"],
                            )
                    else:
                        # No cloud fallback enabled/available
                        return ParseResult(
                            success=False,
                            document_type=self.parser.DOCUMENT_TYPE,
                            file_hash=self.parser.compute_file_hash(file_path),
                            errors=[f"Local OCR failed: {str(local_ocr_error)}"],
                        )
                
                yield ParseProgress(
                    status=ParseStatus.EXTRACTING,
                    progress=90,
                    current_step=f"OCR complete. Analyzing {page_count} pages...",
                )
            else:
                yield ParseProgress(
                    status=ParseStatus.EXTRACTING,
                    progress=60,
                    current_step=f"Text extracted. Analyzing {page_count} pages...",
                )
            
            # Parse extracted data
            # (In a real refined system, we'd pass extracted text/data directly)
            result = self.parser.parse(file_path)
            
            # Update extraction source if OCR was used
            if len(text.strip()) >= 50 and result.success:
                # result.extraction_source = "ocr" # Base class needs update or this is set in parser
                pass

            # Apply PII scrubbing to raw data if it contains transactions
            if result.success and "transactions" in result.raw_data:
                for txn in result.raw_data["transactions"]:
                    if "description" in txn:
                        txn["description"] = self.pii_scrubber.scrub_text(txn["description"])
            
            processing_time = int((time.time() - start_time) * 1000)
            result.processing_time_ms = processing_time
            
            yield ParseProgress(
                status=ParseStatus.COMPLETE,
                progress=100,
                current_step="Extraction complete!",
                partial_results=result.to_dict(),
            )
            
            return result

        # Fallback for other file types (images, txt, etc.) handled by GenericParser
        yield ParseProgress(
            status=ParseStatus.EXTRACTING,
            progress=20,
            current_step=f"Processing {ext} file...",
        )
        result = self.parser.parse(file_path)
        yield ParseProgress(
            status=ParseStatus.COMPLETE,
            progress=100,
            current_step="Processing complete",
            partial_results=result.to_dict(),
        )
        return result

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from api.ingestion.extractors.ocr_local import OCRLocalExtractor
from api.ingestion.pipeline import ExtractionPipeline
from api.ingestion.parsers.base import BaseParser, DocumentType, ParseStatus, ParseResult

class MockParser(BaseParser):
    SUPPORTED_EXTENSIONS = [".pdf"]
    DOCUMENT_TYPE = DocumentType.FORM_16
    def detect(self, file_path): return True, 1.0
    def parse(self, file_path):
        from api.ingestion.parsers.base import ParseResult
        return ParseResult(success=True, document_type=self.DOCUMENT_TYPE, file_hash="abc")

def test_ocr_extractor_streaming_mock():
    # Force available for test
    with patch('api.ingestion.extractors.ocr_local.convert_from_path') as mock_convert, \
         patch('api.ingestion.extractors.ocr_local.pytesseract') as mock_tess:
        
        extractor = OCRLocalExtractor()
        extractor.available = True
        
        mock_convert.return_value = [MagicMock(), MagicMock()] # 2 pages
        mock_tess.image_to_string.side_effect = ["Page 1 text", "Page 2 text"]
        
        text, pages = extractor.extract(Path("test.pdf"))
        
        assert pages == 2
        assert "Page 1 text" in text
        assert "Page 2 text" in text

def test_pipeline_ocr_fallback():
    parser = MockParser()
    pipeline = ExtractionPipeline(parser)
    
    with patch.object(pipeline.text_extractor, 'extract', return_value=("", 1)), \
         patch.object(pipeline.ocr_extractor, 'extract_streaming') as mock_ocr_stream:
        
        # Mock OCR stream updates
        mock_ocr_stream.return_value = iter([
            {"page": 1, "total": 1, "status": "OCR Page 1"}
        ])
        # The generator needs to return a value via StopIteration
        # But for simplicity, we can mock the entire process or just check logic
        
        # Let's adjust OCRLocalExtractor to make it easier to mock or just mock extract_streaming
        def mock_gen(*args):
             yield {"page": 1, "total": 1, "status": "OCR Page 1"}
             return "OCR Text", 1
             
        pipeline.ocr_extractor.extract_streaming = mock_gen
        
        gen = pipeline.process_streaming(Path("scanned.pdf"))
        steps = list(gen)
        
        # Check if "Scanned PDF detected" step exists
        assert any("Scanned PDF detected" in step.current_step for step in steps)
        assert any(step.status == ParseStatus.COMPLETE for step in steps)

if __name__ == "__main__":
    pytest.main([__file__])

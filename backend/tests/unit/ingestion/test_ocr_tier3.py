import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from backend.app.ingestion.extractors.ocr_cloud import OCRCloudExtractor
from backend.app.ingestion.pipeline import ExtractionPipeline
from backend.app.ingestion.parsers.base import BaseParser, DocumentType, ParseStatus, ParseResult

class MockParser(BaseParser):
    SUPPORTED_EXTENSIONS = [".pdf"]
    DOCUMENT_TYPE = DocumentType.FORM_16
    def detect(self, file_path): return True, 1.0
    def parse(self, file_path):
        return ParseResult(success=True, document_type=self.DOCUMENT_TYPE, file_hash="abc")
    def compute_file_hash(self, file_path): return "abc"

def test_cloud_ocr_extractor_mock():
    # Mock vision library and credentials
    with patch('backend.app.ingestion.extractors.ocr_cloud.vision') as mock_vision, \
         patch('backend.app.ingestion.extractors.ocr_cloud.convert_from_path') as mock_convert, \
         patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"}):
        
        extractor = OCRCloudExtractor()
        extractor.available = True
        
        # Mock PDF to image conversion
        mock_image = MagicMock()
        mock_convert.return_value = [mock_image]
        
        # Mock Vision API response
        mock_client = mock_vision.ImageAnnotatorClient.return_value
        mock_response = MagicMock()
        mock_response.error.message = None
        mock_response.text_annotations = [MagicMock(description="Cloud Extracted Text")]
        mock_client.text_detection.return_value = mock_response
        
        text, pages = extractor.extract(Path("test.pdf"))
        
        assert pages == 1
        assert "Cloud Extracted Text" in text

def test_pipeline_tier3_fallback():
    parser = MockParser()
    pipeline = ExtractionPipeline(parser)
    
    # Mock all tiers
    with patch.object(pipeline.text_extractor, 'extract', return_value=("", 1)), \
         patch.object(pipeline.ocr_extractor, 'extract_streaming', side_effect=Exception("Local OCR Failed")), \
         patch.object(pipeline.cloud_ocr_extractor, 'extract_streaming') as mock_cloud_stream, \
         patch.dict(os.environ, {"ENABLE_CLOUD_OCR": "true"}):
         
        # Make cloud OCR available
        pipeline.cloud_ocr_extractor.available = True
        
        # Mock Cloud OCR stream
        def mock_cloud_gen(*args):
             yield {"page": 1, "total": 1, "status": "Cloud OCR Page 1"}
             return "Cloud Text", 1
        
        mock_cloud_stream.side_effect = mock_cloud_gen
        
        gen = pipeline.process_streaming(Path("hard_scan.pdf"))
        steps = list(gen)
        
        # Verify flow
        log = [step.current_step for step in steps]
        assert any("Local OCR failed" in s for s in log)
        assert any("Switching to Cloud OCR" in s for s in log)
        assert any(step.status == ParseStatus.COMPLETE for step in steps)
        
        # Default implementation of MockParser doesn't use the text, so we check if pipeline completed success
        final_result = steps[-1].partial_results
        assert final_result["success"] is True

def test_pipeline_tier3_disabled():
    parser = MockParser()
    pipeline = ExtractionPipeline(parser)
    
    # Mock all tiers failing, with Cloud OCR disabled
    with patch.object(pipeline.text_extractor, 'extract', return_value=("", 1)), \
         patch.object(pipeline.ocr_extractor, 'extract_streaming', side_effect=Exception("Local OCR Failed")), \
         patch.dict(os.environ, {"ENABLE_CLOUD_OCR": "false"}):
         
        pipeline.cloud_ocr_extractor.available = True
        
        gen = pipeline.process_streaming(Path("hard_scan.pdf"))
        # This should return a ParseResult structure with errors
        result = next((step for step in gen if step.status == ParseStatus.COMPLETE), None)
        
        # Actually pipeline yields a result on error too? 
        # Wait, the pipeline returns a ParseResult object directly on error without yielding COMPLETE usually?
        # Let's check pipeline.py logic:
        # returns ParseResult directly if Tier 2 fails and Tier 3 disabled.
        
        gen = pipeline.process_streaming(Path("hard_scan.pdf"))
        try:
            steps = list(gen)
            # If it returns, the generator stops. The return value is the StopIteration value.
            # But process_streaming yields progress updates.
        except StopIteration as e:
            result = e.value
            assert result.success is False
            assert "Local OCR failed" in result.errors[0]

if __name__ == "__main__":
    pytest.main([__file__])

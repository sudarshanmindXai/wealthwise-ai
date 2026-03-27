import pytest
from api.ingestion.utils.pii_mask import PIIScrubber

class TestPIIScrubber:
    
    def test_mask_pan(self):
        text = "My PAN is ABCDE1234F and yours is FGHIJ5678K."
        cleaned = PIIScrubber.mask_pan(text)
        assert "XXXXX1234X" in cleaned
        assert "XXXXX5678X" in cleaned
        assert "ABCDE" not in cleaned
        
    def test_mask_email(self):
        text = "Contact support@wealthwise.com for help."
        cleaned = PIIScrubber.mask_email(text)
        assert "s***@wealthwise.com" in cleaned
        assert "support@" not in cleaned
        
    def test_mask_phone(self):
        text = "Call me at +91 9876543210 immediately."
        cleaned = PIIScrubber.mask_phone(text)
        assert "XXXXXXXXXX" in cleaned
        assert "9876543210" not in cleaned
        
    def test_scrub_all(self):
        text = """
        Name: Vikram Rathore
        PAN: ABCDE1234F
        Email: vikram@example.com
        Phone: 9876543210
        """
        cleaned = PIIScrubber.scrub_text(text)
        assert "XXXXX1234X" in cleaned
        assert "v***@example.com" in cleaned
        assert "XXXXXXXXXX" in cleaned

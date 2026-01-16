"""
WealthWise AI - Cloud OCR Extractor
====================================
Uses Google Cloud Vision API for premium OCR extraction.
"""

import os
import logging
import io
from pathlib import Path
from typing import Optional, Generator

try:
    from google.cloud import vision
    from google.oauth2 import service_account
    from pdf2image import convert_from_path
except ImportError:
    vision = None
    service_account = None
    convert_from_path = None

class OCRCloudExtractor:
    """Handles OCR extraction using Google Cloud Vision"""
    
    def __init__(self):
        self.available = False
        if vision:
            # Check for credentials
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_API_KEY"):
                self.available = True
            else:
                logging.warning("Google Cloud credentials not found. Cloud OCR disabled.")
        else:
            logging.warning("google-cloud-vision library not installed.")

    def extract_streaming(self, file_path: Path) -> Generator[dict, None, tuple[str, int]]:
        """
        Extract text from PDF using Google Cloud Vision.
        Note: GCV for PDF handles files differently (async usually), 
        but for simplicity in this tier we might convert to images first if pdf2image is available,
        or use GCV's PDF support. 
        
        For this implementation, we'll reuse the image conversion approach for consistency with local OCR,
        sending pages to GCV.
        """
        if not self.available:
            raise ImportError("Cloud OCR unavailable. Check dependencies and credentials.")

        try:
            client = vision.ImageAnnotatorClient()
        except Exception:
             raise ImportError("Failed to initialize Google Vision Client.")

        text = ""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path)
            total_pages = len(images)
            
            for i, image in enumerate(images):
                page_num = i + 1
                yield {
                    "page": page_num,
                    "total": total_pages,
                    "status": f"Sending page {page_num} to Cloud OCR..."
                }
                
                # Convert PIL image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                content = img_byte_arr.getvalue()
                
                image_content = vision.Image(content=content)
                response = client.text_detection(image=image_content)
                
                if response.error.message:
                    raise Exception(f"Google Vision API Error: {response.error.message}")
                    
                if response.text_annotations:
                    # The first annotation is the full text
                    text += response.text_annotations[0].description + "\n"
                    
        except Exception as e:
            logging.error(f"Cloud OCR extraction failed: {str(e)}")
            raise e
            
        return text, total_pages

    def extract(self, file_path: Path) -> tuple[str, int]:
        gen = self.extract_streaming(file_path)
        try:
            while True:
                next(gen)
        except StopIteration as e:
            return e.value

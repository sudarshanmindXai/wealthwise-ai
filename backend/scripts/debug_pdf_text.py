import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd() / "wealthwise/backend"))

from app.ingestion.extractors.pdf_text import PDFTextExtractor

def debug_pdf(filename):
    file_path = Path(filename).resolve()
    print(f"Reading: {file_path}")
    
    extractor = PDFTextExtractor(library="pdfplumber")
    text, pages = extractor.extract(file_path)
    
    print("-" * 50)
    print(text)
    print("-" * 50)

if __name__ == "__main__":
    debug_pdf("wealthwise/backend/sample_docs/form16_vikram.pdf")

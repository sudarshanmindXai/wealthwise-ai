"""
WealthWise API - FastAPI Backend

Provides document ingestion, parsing, and tax calculation endpoints.
Supports multi-file uploads with automatic document type detection.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uvicorn
import os
import sys
import io
from datetime import datetime

# Add root to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest.document_detector import DocumentType, detect_document_type, get_document_description
from src.ingest.universal_extractor import extract_document_data, map_extracted_to_taxfacts

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'xls', 'jpg', 'jpeg', 'png'}

app = FastAPI(
    title="WealthWise API",
    description="Document ingestion and tax calculation API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class DocumentResult(BaseModel):
    filename: str
    size_bytes: int
    detected_type: str
    type_description: str
    confidence: float
    status: str  # 'success', 'error', 'needs_review'
    extracted_data: Optional[Dict[str, Any]] = None
    tax_facts: Optional[Dict[str, Any]] = None
    warnings: List[str] = []
    error: Optional[str] = None


class IngestResponse(BaseModel):
    total_files: int
    successful: int
    failed: int
    needs_review: int
    files: List[DocumentResult]
    processing_time_ms: int


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate file type and size."""
    # Check extension
    if not file.filename:
        return False, "Filename is required"
    
    ext = file.filename.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, ""


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "WealthWise API",
        "version": "1.0.0",
        "endpoints": {
            "ingest": "/ingest - POST multi-file document upload",
            "detect": "/detect - POST single file type detection",
            "calculate": "/calculate - POST tax calculation"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    Ingest multiple documents for processing.
    
    Supports: PDF, CSV, XLSX, XLS, JPG, PNG
    Max file size: 10MB per file
    
    Returns detection results and extracted data for each file.
    """
    start_time = datetime.now()
    results: List[DocumentResult] = []
    successful = 0
    failed = 0
    needs_review = 0
    
    for file in files:
        try:
            # Validate file
            is_valid, error_msg = validate_file(file)
            if not is_valid:
                results.append(DocumentResult(
                    filename=file.filename or "unknown",
                    size_bytes=0,
                    detected_type="unknown",
                    type_description="Unknown",
                    confidence=0.0,
                    status="error",
                    error=error_msg
                ))
                failed += 1
                continue
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Check size
            if file_size > MAX_FILE_SIZE:
                results.append(DocumentResult(
                    filename=file.filename,
                    size_bytes=file_size,
                    detected_type="unknown",
                    type_description="Unknown",
                    confidence=0.0,
                    status="error",
                    error=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
                ))
                failed += 1
                continue
            
            # Get file extension
            ext = file.filename.split('.')[-1].lower()
            
            # Detect document type
            detection = detect_document_type(content, file.filename, ext)
            doc_type_str = detection.get("document_type", "unknown")
            confidence = detection.get("confidence", 0.0)
            
            # Get document type enum
            try:
                doc_type = DocumentType(doc_type_str)
            except ValueError:
                doc_type = DocumentType.UNKNOWN
            
            type_description = get_document_description(doc_type)
            
            # Determine status based on confidence
            if confidence >= 0.8:
                status = "success"
            elif confidence >= 0.5:
                status = "needs_review"
                needs_review += 1
            else:
                status = "needs_review"
                needs_review += 1
            
            # Extract data if confidence is reasonable
            extracted_data = {}
            tax_facts = {}
            warnings = detection.get("suggestions", [])
            
            if confidence >= 0.5 and doc_type != DocumentType.UNKNOWN:
                try:
                    extraction_result = extract_document_data(
                        content, doc_type, file.filename, ext
                    )
                    extracted_data = extraction_result.get("extracted_data", {})
                    warnings.extend(extraction_result.get("warnings", []))
                    
                    # Map to tax facts
                    tax_facts = map_extracted_to_taxfacts(extracted_data, doc_type)
                    
                    if extraction_result.get("confidence", 0) >= 0.7:
                        status = "success"
                        successful += 1
                    else:
                        status = "needs_review"
                        if confidence >= 0.8:
                            needs_review += 1
                except Exception as e:
                    warnings.append(f"Extraction error: {str(e)}")
                    status = "needs_review"
                    needs_review += 1
            else:
                if status == "success":
                    successful += 1
            
            results.append(DocumentResult(
                filename=file.filename,
                size_bytes=file_size,
                detected_type=doc_type_str,
                type_description=type_description,
                confidence=confidence,
                status=status,
                extracted_data=extracted_data if extracted_data else None,
                tax_facts=tax_facts if tax_facts else None,
                warnings=warnings
            ))
            
        except Exception as e:
            results.append(DocumentResult(
                filename=file.filename or "unknown",
                size_bytes=0,
                detected_type="unknown",
                type_description="Unknown",
                confidence=0.0,
                status="error",
                error=str(e)
            ))
            failed += 1
    
    processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
    
    return IngestResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        needs_review=needs_review,
        files=results,
        processing_time_ms=processing_time
    )


@app.post("/detect")
async def detect_document(file: UploadFile = File(...)):
    """
    Detect the type of a single document without full extraction.
    Useful for quick validation before upload.
    """
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    content = await file.read()
    ext = file.filename.split('.')[-1].lower()
    
    detection = detect_document_type(content, file.filename, ext)
    
    try:
        doc_type = DocumentType(detection.get("document_type", "unknown"))
    except ValueError:
        doc_type = DocumentType.UNKNOWN
    
    return {
        "filename": file.filename,
        "detected_type": detection.get("document_type", "unknown"),
        "type_description": get_document_description(doc_type),
        "confidence": detection.get("confidence", 0.0),
        "reasoning": detection.get("reasoning", ""),
        "suggestions": detection.get("suggestions", [])
    }


@app.post("/calculate")
def calculate_tax(profile: Dict[str, Any]):
    """
    Calculate tax based on extracted profile data.
    Compares Old vs New regime and provides recommendation.
    """
    # Mock calculation - will integrate with actual tax engine
    gross_income = profile.get("salary_gross", 0) + profile.get("business_income", 0)
    
    # Simple placeholder calculation
    old_regime_tax = max(0, (gross_income - 250000) * 0.2)
    new_regime_tax = max(0, (gross_income - 300000) * 0.15)
    
    return {
        "old_regime": {
            "tax": int(old_regime_tax),
            "effective_rate": round(old_regime_tax / max(gross_income, 1) * 100, 2)
        },
        "new_regime": {
            "tax": int(new_regime_tax),
            "effective_rate": round(new_regime_tax / max(gross_income, 1) * 100, 2)
        },
        "savings": int(abs(old_regime_tax - new_regime_tax)),
        "recommendation": "NEW" if new_regime_tax < old_regime_tax else "OLD"
    }


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

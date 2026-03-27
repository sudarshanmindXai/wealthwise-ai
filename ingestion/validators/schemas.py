"""
WealthWise AI - Ingestion Schemas
=================================
Pydantic models for the ingestion pipeline.
"""

from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime

# --- Responses ---

class UploadResponse(BaseModel):
    """Response for single file upload"""
    task_id: str
    filename: str
    status: str
    message: str

class BatchUploadResponse(BaseModel):
    """Response for batch upload"""
    batch_id: str
    tasks: list[dict]
    total_files: int

class TaskStatus(BaseModel):
    """Status of a parsing task"""
    task_id: str
    filename: str
    status: str
    progress: int
    current_step: str
    document_type: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None

class BatchStatus(BaseModel):
    """Status of a batch upload"""
    batch_id: str
    overall_progress: int
    total_files: int
    completed_files: int
    tasks: list[TaskStatus]
    aggregated: Optional[dict] = None

# --- Internal ---

class ExtractionField(BaseModel):
    """A single extracted field with confidence"""
    name: str
    value: Any
    confidence: float
    source: str = "text_extract"  # text_extract, ocr, ml
    needs_review: bool = False

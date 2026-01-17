"""
WealthWise AI - Ingestion API Router
=====================================
FastAPI endpoints for document upload and parsing.

Endpoints:
- POST /upload - Single file upload
- POST /batch - Multi-file upload
- GET /status/{task_id} - Check parsing status
- GET /batch/{batch_id}/status - Check batch status
"""

import uuid
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .parsers import (
    BaseParser,
    ParseResult,
    ParseProgress,
    ParseStatus,
    ExtractionField,
    Form16Parser,
    BankStatementParser,
    SalarySlipParser,
    ELSSReceiptParser,
    ZerodhaPnLParser,

    CASStatementParser,
    GenericParser,
)
from .parsers.base import DocumentType, detect_document_type


router = APIRouter(prefix="/ingest", tags=["ingestion"])


from .store import tasks as _tasks, batches as _batches

# Temp directory for uploads
UPLOAD_DIR = Path(tempfile.gettempdir()) / "wealthwise_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# Request/Response Models

from .validators.schemas import (
    UploadResponse,
    BatchUploadResponse,
    TaskStatus,
    BatchStatus,
)


# Helper functions

def get_parser_for_file(file_path: Path) -> Optional[BaseParser]:
    """Get appropriate parser for a file by checking detection confidence"""
    parsers = [
        Form16Parser(),
        BankStatementParser(),
        SalarySlipParser(),
        ELSSReceiptParser(),
        ZerodhaPnLParser(),

        CASStatementParser(),
        GenericParser(),
    ]
    
    best_parser = None
    best_confidence = 0.0
    
    for parser in parsers:
        try:
            is_match, confidence = parser.detect(file_path)
            print(f"DEBUG: Parser {parser.__class__.__name__} -> match={is_match}, conf={confidence}")
            if is_match and confidence > best_confidence:
                best_confidence = confidence
                best_parser = parser
        except Exception:
            continue
            
    return best_parser


from .parsers.base import DocumentType
from .pipeline import ExtractionPipeline
from fastapi import WebSocket, WebSocketDisconnect


@router.websocket("/stream/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    Stream progress updates via WebSocket.
    """
    await websocket.accept()
    try:
        while True:
            if task_id in _tasks:
                task = _tasks[task_id]
                await websocket.send_json({
                    "status": task["status"],
                    "progress": task["progress"],
                    "current_step": task["current_step"],
                    "partial_results": task.get("partial_results"),
                })
                if task["status"] in ["complete", "error", "failed"]:
                    break
            else:
                await websocket.send_json({"error": "Task not found"})
                break
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


async def process_file_async(task_id: str, file_path: Path, filename: str):
    """Background task to process a file using the pipeline"""
    try:
        # Update status - detecting
        _tasks[task_id]["status"] = "detecting"
        _tasks[task_id]["progress"] = 10
        
        # Get parser
        parser = get_parser_for_file(file_path)
        
        if not parser:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = "Could not detect document type."
            _tasks[task_id]["progress"] = 100
            return
        
        _tasks[task_id]["document_type"] = parser.DOCUMENT_TYPE.value
        
        # Initialize pipeline
        pipeline = ExtractionPipeline(parser)
        
        # Process with streaming
        for progress_update in pipeline.process_streaming(file_path):
            # Update task state
            current_status = getattr(progress_update.status, "value", str(progress_update.status))
            
            # Only update status immediately if NOT complete (to avoid race condition)
            if current_status != "complete":
                _tasks[task_id]["status"] = current_status
            
            _tasks[task_id]["progress"] = progress_update.progress
            _tasks[task_id]["current_step"] = progress_update.current_step
            
            if progress_update.partial_results:
                _tasks[task_id]["partial_results"] = progress_update.partial_results
            
            # Small delay to allow WS to pick up changes
            await asyncio.sleep(0.1)
            
            # Handle completion atomically
            if current_status == "complete":
                _tasks[task_id]["result"] = progress_update.partial_results
                _tasks[task_id]["status"] = "complete"  # Set status LAST
        
    except Exception as e:
        import traceback
        _tasks[task_id]["status"] = "error"
        _tasks[task_id]["error"] = str(e)
        _tasks[task_id]["traceback"] = traceback.format_exc()
        _tasks[task_id]["progress"] = 100


# Endpoints

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a single file for parsing.
    
    Returns a task_id to track progress.
    """
    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum size is 10MB.")
    
    # Validate extension
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    allowed_extensions = [".pdf", ".csv", ".xlsx", ".xls", ".txt", ".jpg", ".png", ".jpeg"]
    
    if ext not in allowed_extensions:
        raise HTTPException(
            400, 
            f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save to temp file
    task_id = str(uuid.uuid4())[:8]
    file_path = UPLOAD_DIR / f"{task_id}_{filename}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Initialize task
    _tasks[task_id] = {
        "task_id": task_id,
        "filename": filename,
        "file_path": str(file_path),
        "status": "pending",
        "progress": 0,
        "current_step": "Queued for processing",
        "document_type": None,
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
    }
    
    # Start background processing
    background_tasks.add_task(process_file_async, task_id, file_path, filename)
    
    return UploadResponse(
        task_id=task_id,
        filename=filename,
        status="pending",
        message="File uploaded successfully. Processing started.",
    )


@router.post("/batch", response_model=BatchUploadResponse)
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
):
    """
    Upload multiple files for batch parsing.
    
    Returns a batch_id and individual task_ids.
    """
    if len(files) > 20:
        raise HTTPException(400, "Maximum 20 files per batch.")
    
    batch_id = str(uuid.uuid4())[:8]
    tasks = []
    
    for file in files:
        # Validate each file
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            continue  # Skip files that are too large
        
        filename = file.filename or "unknown"
        ext = Path(filename).suffix.lower()
        allowed_extensions = [".pdf", ".csv", ".xlsx", ".xls"]
        
        if ext not in allowed_extensions:
            continue  # Skip unsupported files
        
        # Save to temp file
        task_id = str(uuid.uuid4())[:8]
        file_path = UPLOAD_DIR / f"{task_id}_{filename}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Initialize task
        _tasks[task_id] = {
            "task_id": task_id,
            "filename": filename,
            "file_path": str(file_path),
            "status": "pending",
            "progress": 0,
            "current_step": "Queued for processing",
            "document_type": None,
            "result": None,
            "error": None,
            "batch_id": batch_id,
            "created_at": datetime.now().isoformat(),
        }
        
        tasks.append({
            "task_id": task_id,
            "filename": filename,
            "status": "pending",
        })
        
        # Start background processing
        background_tasks.add_task(process_file_async, task_id, file_path, filename)
    
    # Initialize batch
    _batches[batch_id] = {
        "batch_id": batch_id,
        "task_ids": [t["task_id"] for t in tasks],
        "created_at": datetime.now().isoformat(),
    }
    
    return BatchUploadResponse(
        batch_id=batch_id,
        tasks=tasks,
        total_files=len(tasks),
    )


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a parsing task."""
    if task_id not in _tasks:
        raise HTTPException(404, f"Task not found: {task_id}")
    
    task = _tasks[task_id]
    
    return TaskStatus(
        task_id=task["task_id"],
        filename=task["filename"],
        status=task["status"],
        progress=task["progress"],
        current_step=task["current_step"],
        document_type=task.get("document_type"),
        result=task.get("result"),
        error=task.get("error"),
    )


@router.get("/batch/{batch_id}/status", response_model=BatchStatus)
async def get_batch_status(batch_id: str):
    """Get the status of a batch upload."""
    if batch_id not in _batches:
        raise HTTPException(404, f"Batch not found: {batch_id}")
    
    batch = _batches[batch_id]
    task_ids = batch["task_ids"]
    
    tasks = []
    completed = 0
    total_progress = 0
    
    # Collect aggregated data
    aggregated = {
        "bank_statements": {
            "total_credits": 0,
            "total_debits": 0,
            "transaction_count": 0,
        },
        "form16": {
            "total_gross_salary": 0,
            "total_tds": 0,
            "employers": [],
        },
    }
    
    for task_id in task_ids:
        task = _tasks.get(task_id, {})
        
        task_status = TaskStatus(
            task_id=task.get("task_id", task_id),
            filename=task.get("filename", "unknown"),
            status=task.get("status", "unknown"),
            progress=task.get("progress", 0),
            current_step=task.get("current_step", ""),
            document_type=task.get("document_type"),
            result=task.get("result"),
            error=task.get("error"),
        )
        tasks.append(task_status)
        
        total_progress += task.get("progress", 0)
        
        if task.get("status") == "complete":
            completed += 1
            
            # Aggregate results
            result = task.get("result", {})
            doc_type = task.get("document_type")
            
            if doc_type == "bank_statement":
                for field in result.get("fields", []):
                    if field["name"] == "total_credits":
                        aggregated["bank_statements"]["total_credits"] += field["value"] or 0
                    elif field["name"] == "total_debits":
                        aggregated["bank_statements"]["total_debits"] += field["value"] or 0
                    elif field["name"] == "transaction_count":
                        aggregated["bank_statements"]["transaction_count"] += field["value"] or 0
            
            elif doc_type == "form_16":
                for field in result.get("fields", []):
                    if field["name"] == "gross_salary":
                        aggregated["form16"]["total_gross_salary"] += field["value"] or 0
                    elif field["name"] == "tds_deducted":
                        aggregated["form16"]["total_tds"] += field["value"] or 0
                    elif field["name"] == "employer_name" and field["value"]:
                        aggregated["form16"]["employers"].append(field["value"])
    
    overall_progress = total_progress // len(task_ids) if task_ids else 0
    
    return BatchStatus(
        batch_id=batch_id,
        overall_progress=overall_progress,
        total_files=len(task_ids),
        completed_files=completed,
        tasks=tasks,
        aggregated=aggregated,
    )


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its associated file."""
    if task_id not in _tasks:
        raise HTTPException(404, f"Task not found: {task_id}")
    
    task = _tasks[task_id]
    
    # Delete file
    file_path = Path(task.get("file_path", ""))
    if file_path.exists():
        file_path.unlink()
    
    # Remove task
    del _tasks[task_id]
    
    return {"message": f"Task {task_id} deleted"}

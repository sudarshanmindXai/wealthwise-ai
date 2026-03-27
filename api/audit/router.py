"""
WealthWise AI - Audit API Router
=================================
API endpoints for audit trail and provenance viewing.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .store import (
    get_all_events,
    get_events_for_task,
    get_provenance_for_task,
    get_event_summary,
    AuditEvent,
    FieldProvenance,
)


router = APIRouter(prefix="/audit", tags=["audit"])


# Response Models

class AuditEventResponse(BaseModel):
    id: str
    event_type: str
    timestamp: str
    task_id: str
    filename: str
    document_type: Optional[str]
    details: dict


class ProvenanceResponse(BaseModel):
    field_name: str
    value: str
    confidence: float
    source: str
    extraction_method: str


class SummaryResponse(BaseModel):
    total_events: int
    by_event_type: dict
    by_document_type: dict
    unique_tasks: int


# Endpoints

@router.get("/events", response_model=List[AuditEventResponse])
async def list_audit_events(
    limit: int = 100,
    task_id: Optional[str] = None,
    event_type: Optional[str] = None,
):
    """
    List audit events with optional filtering.
    
    - **limit**: Maximum number of events to return
    - **task_id**: Filter by specific task
    - **event_type**: Filter by event type
    """
    events = get_all_events()
    
    # Apply filters
    if task_id:
        events = [e for e in events if e.task_id == task_id]
    if event_type:
        events = [e for e in events if e.event_type.value == event_type]
    
    # Sort by timestamp descending (newest first)
    events = sorted(events, key=lambda e: e.timestamp, reverse=True)
    
    # Limit
    events = events[:limit]
    
    return [
        AuditEventResponse(
            id=e.id,
            event_type=e.event_type.value,
            timestamp=e.timestamp,
            task_id=e.task_id,
            filename=e.filename,
            document_type=e.document_type,
            details=e.details,
        )
        for e in events
    ]


@router.get("/events/{task_id}", response_model=List[AuditEventResponse])
async def get_task_events(task_id: str):
    """Get all audit events for a specific task/document."""
    events = get_events_for_task(task_id)
    
    if not events:
        raise HTTPException(404, f"No events found for task: {task_id}")
    
    return [
        AuditEventResponse(
            id=e.id,
            event_type=e.event_type.value,
            timestamp=e.timestamp,
            task_id=e.task_id,
            filename=e.filename,
            document_type=e.document_type,
            details=e.details,
        )
        for e in events
    ]


@router.get("/provenance/{task_id}", response_model=List[ProvenanceResponse])
async def get_task_provenance(task_id: str):
    """
    Get field-level extraction provenance for a task.
    
    Shows where each extracted value came from (source, confidence, method).
    """
    provenance = get_provenance_for_task(task_id)
    
    return [
        ProvenanceResponse(
            field_name=p.field_name,
            value=str(p.value),
            confidence=p.confidence,
            source=p.source,
            extraction_method=p.extraction_method,
        )
        for p in provenance
    ]


@router.get("/summary", response_model=SummaryResponse)
async def get_audit_summary():
    """Get audit trail summary statistics."""
    return get_event_summary()

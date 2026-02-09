"""
WealthWise AI - Audit Trail Storage
====================================
In-memory storage for audit events and provenance tracking.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class AuditEventType(str, Enum):
    """Types of audit events"""
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_DETECTING = "document_detecting"
    DOCUMENT_DETECTED = "document_detected"
    DOCUMENT_PARSING = "document_parsing"
    DOCUMENT_PARSED = "document_parsed"
    DOCUMENT_ERROR = "document_error"
    FIELD_EXTRACTED = "field_extracted"
    USER_CLASSIFICATION = "user_classification"


@dataclass
class AuditEvent:
    """A single audit event"""
    id: str
    event_type: AuditEventType
    timestamp: str
    task_id: str
    filename: str
    document_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "filename": self.filename,
            "document_type": self.document_type,
            "details": self.details,
        }


@dataclass  
class FieldProvenance:
    """Provenance tracking for an extracted field"""
    field_name: str
    value: Any
    confidence: float
    source: str  # "text_extract", "ocr", "inferred"
    extraction_method: str
    page_number: Optional[int] = None
    bounding_box: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


# In-memory storage
_audit_events: List[AuditEvent] = []
_provenance_store: Dict[str, List[FieldProvenance]] = {}  # task_id -> fields
_event_counter = 0


def generate_event_id() -> str:
    global _event_counter
    _event_counter += 1
    return f"evt_{_event_counter:06d}"


def log_event(
    event_type: AuditEventType,
    task_id: str,
    filename: str,
    document_type: Optional[str] = None,
    details: Optional[Dict] = None,
) -> AuditEvent:
    """Log an audit event"""
    event = AuditEvent(
        id=generate_event_id(),
        event_type=event_type,
        timestamp=datetime.now().isoformat(),
        task_id=task_id,
        filename=filename,
        document_type=document_type,
        details=details or {},
    )
    _audit_events.append(event)
    return event


def log_provenance(
    task_id: str,
    field_name: str,
    value: Any,
    confidence: float,
    source: str = "text_extract",
    extraction_method: str = "regex",
) -> FieldProvenance:
    """Log field extraction provenance"""
    prov = FieldProvenance(
        field_name=field_name,
        value=value,
        confidence=confidence,
        source=source,
        extraction_method=extraction_method,
    )
    if task_id not in _provenance_store:
        _provenance_store[task_id] = []
    _provenance_store[task_id].append(prov)
    return prov


def get_all_events() -> List[AuditEvent]:
    """Get all audit events"""
    return _audit_events


def get_events_for_task(task_id: str) -> List[AuditEvent]:
    """Get audit events for a specific task"""
    return [e for e in _audit_events if e.task_id == task_id]


def get_provenance_for_task(task_id: str) -> List[FieldProvenance]:
    """Get field provenance for a task"""
    return _provenance_store.get(task_id, [])


def get_event_summary() -> Dict:
    """Get summary statistics"""
    by_type = {}
    by_doc_type = {}
    
    for event in _audit_events:
        # Count by event type
        et = event.event_type.value
        by_type[et] = by_type.get(et, 0) + 1
        
        # Count by document type
        if event.document_type:
            by_doc_type[event.document_type] = by_doc_type.get(event.document_type, 0) + 1
    
    return {
        "total_events": len(_audit_events),
        "by_event_type": by_type,
        "by_document_type": by_doc_type,
        "unique_tasks": len(set(e.task_id for e in _audit_events)),
    }

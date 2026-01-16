"""
WealthWise AI - Document Ingestion Module
==========================================
Handles parsing of financial documents:
- Form 16 (Part B) - Salary & TDS
- Bank Statements - CSV/XLSX/PDF
- CAS Statements - Mutual Fund holdings
- Broker P&L - Capital gains

Usage:
    from app.ingestion import router
    app.include_router(router)
"""

from .router import router
from .parsers import (
    BaseParser,
    ParseResult,
    ParseProgress,
    ExtractionField,
    Form16Parser,
    BankStatementParser,
)
from .parsers.base import DocumentType, ParseStatus

__all__ = [
    "router",
    "BaseParser",
    "ParseResult",
    "ParseProgress",
    "ExtractionField",
    "Form16Parser",
    "BankStatementParser",
    "DocumentType",
    "ParseStatus",
]

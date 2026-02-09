"""
WealthWise AI - FastAPI Entry Point
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from .routers import chat
from .ingestion.router import router as ingestion_router

app = FastAPI(
    title="WealthWise AI",
    description="Agentic Tax Auditor & Optimization Engine",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "WealthWise AI API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(ingestion_router, prefix="/api/v1", tags=["ingestion"])

# Late import to avoid circular dep issues if any
from .routers import analysis, review, report
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(review.router, prefix="/api/v1", tags=["review"])
app.include_router(report.router, prefix="/api/v1", tags=["report"])

from .routers import output
app.include_router(output.router, prefix="/api/v1")

# Audit Trail
from .audit import audit_router
app.include_router(audit_router, prefix="/api/v1", tags=["audit"])

# Serve Audit UI at /audit-ui
AUDIT_UI_DIR = Path(__file__).parent / "audit-ui"

@app.get("/audit-ui")
async def serve_audit_ui():
    """Serve the audit trail dashboard"""
    return FileResponse(AUDIT_UI_DIR / "index.html")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)


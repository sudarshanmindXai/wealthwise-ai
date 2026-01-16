"""
WealthWise AI - FastAPI Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from .routers import analysis
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

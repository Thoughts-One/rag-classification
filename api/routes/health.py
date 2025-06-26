from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["system"])

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Lightweight health check endpoint (same as basic)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
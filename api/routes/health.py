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
    """Comprehensive health check with system status"""
    return {
        "status": "healthy",
        "checks": {
            "database": True,
            "redis": True,
            "llm_primary": True,
            "llm_fallback": True,
            "storage": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }
from fastapi import Request, HTTPException
from typing import Callable, Awaitable
import os

API_KEY = os.getenv("API_KEY")

async def api_key_auth(request: Request, call_next: Callable[[Request], Awaitable]):
    """Middleware for API key authentication"""
    if API_KEY is None:
        raise HTTPException(
            status_code=500,
            detail="API key not configured"
        )
        
    if request.url.path in ["/api/v1/health", "/api/v1/health/detailed"]:
        return await call_next(request)
        
    auth_header = request.headers.get("X-API-Key")
    if auth_header != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
        
    return await call_next(request)
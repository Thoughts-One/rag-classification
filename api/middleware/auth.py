from fastapi import Request, HTTPException
from typing import Callable, Awaitable
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY")

async def api_key_auth(request: Request, call_next: Callable[[Request], Awaitable]):
    """Middleware for API key authentication"""
    
    # Debug logging
    logger.info(f"Auth middleware called for path: '{request.url.path}'")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Full URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    if API_KEY is None:
        logger.error("API_KEY environment variable not set!")
        raise HTTPException(
            status_code=500,
            detail="API key not configured"
        )
    
    # Add more paths and check exact matching
    public_paths = ["/", "/api/v1/health", "/api/v1/health/detailed"]
    current_path = request.url.path
    
    logger.info(f"Checking if '{current_path}' is in {public_paths}")
    
    if current_path in public_paths:
        logger.info(f"Path '{current_path}' is public, allowing access")
        return await call_next(request)
    
    # Also check for Render health checks by user agent
    user_agent = request.headers.get("user-agent", "")
    if "Render/1.0" in user_agent:
        logger.info("Render health check detected, allowing access")
        return await call_next(request)
    
    # Check for API key
    auth_header = request.headers.get("X-API-Key")
    logger.info(f"API key present: {auth_header is not None}")
    
    if auth_header != API_KEY:
        logger.warning(f"Invalid API key attempt for path: {current_path}")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.info("API key valid, allowing access")
    return await call_next(request)
from fastapi import Request
from typing import Callable, Awaitable
import logging
import time

logger = logging.getLogger(__name__)

async def request_logger(request: Request, call_next: Callable[[Request], Awaitable]):
    """Middleware for request logging"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    user_agent = request.headers.get("User-Agent", "")
    if "Render/1.0" not in user_agent:
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Process Time: {process_time:.2f}s"
        )
    
    return response
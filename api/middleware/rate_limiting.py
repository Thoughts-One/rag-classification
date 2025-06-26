from fastapi import Request, HTTPException
from typing import Callable, Awaitable
import time
from collections import defaultdict

RATE_LIMIT = 1000  # requests per hour
RATE_LIMIT_WINDOW = 3600  # seconds

request_counts = defaultdict(int)
window_start = time.time()

async def rate_limit_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
    """Middleware for rate limiting"""
    global window_start
    
    current_time = time.time()
    if current_time - window_start > RATE_LIMIT_WINDOW:
        request_counts.clear()
        window_start = current_time
        
    client_ip = request.client.host
    request_counts[client_ip] += 1
    
    if request_counts[client_ip] > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT} requests per hour."
        )
        
    return await call_next(request)
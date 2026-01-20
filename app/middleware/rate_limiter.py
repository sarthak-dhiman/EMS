from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
import os
from typing import Dict


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding-window rate limiter. Not suitable for multi-process production.

    Configure with env `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`.
    """

    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = int(os.getenv("RATE_LIMIT_REQUESTS", max_requests))
        self.window = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", window_seconds))
        self.storage: Dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        # key by client IP
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window

        timestamps = self.storage.get(ip, [])
        # drop old
        timestamps = [t for t in timestamps if t > window_start]
        if len(timestamps) >= self.max_requests:
            return JSONResponse({"detail": "Too many requests"}, status_code=429)

        timestamps.append(now)
        self.storage[ip] = timestamps

        response = await call_next(request)
        return response

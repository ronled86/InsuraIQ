import time
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .settings import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.events = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        q = self.events[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= settings.RATE_LIMIT_PER_MINUTE:
            return Response("Too Many Requests", status_code=429)
        q.append(now)
        response = await call_next(request)
        return response
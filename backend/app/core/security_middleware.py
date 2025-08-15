"""
Security headers middleware for enhanced protection
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    
    def __init__(self, app, enforce_https: bool = False):
        super().__init__(app)
        self.enforce_https = enforce_https
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response, request)
        
        return response
    
    def _add_security_headers(self, response: Response, request: Request) -> None:
        """Add comprehensive security headers"""
        
        # Content Security Policy - Strict policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://unpkg.com",  # Allow PDF.js worker
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "media-src 'none'",
            "object-src 'none'",
            "child-src 'none'",
            "frame-src 'none'",
            "worker-src 'self' blob:",  # Allow PDF.js worker
            "manifest-src 'self'",
            "form-action 'self'",
            "base-uri 'self'",
            "upgrade-insecure-requests"
        ]
        
        if self.enforce_https:
            csp_directives.append("upgrade-insecure-requests")
        
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # HTTP Strict Transport Security (HSTS)
        if self.enforce_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options - Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection - Enable XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy - Control browser features
        permissions_policy = [
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=()",
            "battery=()",
            "camera=()",
            "cross-origin-isolated=()",
            "display-capture=()",
            "document-domain=()",
            "encrypted-media=()",
            "execution-while-not-rendered=()",
            "execution-while-out-of-viewport=()",
            "fullscreen=(self)",
            "geolocation=()",
            "gyroscope=()",
            "keyboard-map=()",
            "magnetometer=()",
            "microphone=()",
            "midi=()",
            "navigation-override=()",
            "payment=()",
            "picture-in-picture=()",
            "publickey-credentials-get=()",
            "screen-wake-lock=()",
            "sync-xhr=()",
            "usb=()",
            "web-share=()",
            "xr-spatial-tracking=()"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_policy)
        
        # Cache Control - Prevent caching of sensitive data
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # X-Robots-Tag - Prevent indexing of API endpoints
        if request.url.path.startswith("/api/"):
            response.headers["X-Robots-Tag"] = "noindex, nofollow, nosnippet, noarchive"
        
        # Server header removal (don't advertise server software)
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # X-Powered-By header removal
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        # Add custom security headers
        response.headers["X-Security-Policy"] = "InsuraIQ-Secure"
        response.headers["X-Content-Security"] = "protected"

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request validation and security checks
    """
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request size for non-file uploads
        if not request.url.path.endswith(("/upload", "/import/pdf")):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 1024 * 1024:  # 1MB for regular requests
                return Response(
                    content="Request too large",
                    status_code=413,
                    headers={"Content-Type": "text/plain"}
                )
        
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-host",
            "x-real-ip", 
            "x-forwarded-proto"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log suspicious activity
                logger.warning(f"Suspicious header detected: {header} = {request.headers[header]}")
        
        # Check User-Agent
        user_agent = request.headers.get("user-agent", "").lower()
        if not user_agent or any(bot in user_agent for bot in ["bot", "crawler", "spider", "scraper"]):
            if request.url.path.startswith("/api/"):
                logger.warning(f"Suspicious User-Agent: {user_agent}")
        
        # Process request
        response = await call_next(request)
        
        # Add request ID for tracking
        import uuid
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        
        return response

class RateLimitEnhancedMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting with additional security features
    """
    
    def __init__(self, app, rate_limit_per_minute: int = 240):
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.request_counts = {}
        self.blocked_ips = set()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return Response(
                content="Access denied",
                status_code=403,
                headers={"Content-Type": "text/plain"}
            )
        
        # Apply rate limiting logic here (simplified)
        # In production, use Redis or proper rate limiting library
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address safely"""
        # Check X-Forwarded-For header (if behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (client IP)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"

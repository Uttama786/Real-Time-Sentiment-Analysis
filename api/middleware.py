"""
API middleware for logging, CORS, and rate limiting
"""
import time
import logging
from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"(completed in {process_time:.3f}s)"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP (TestClient may not set request.client)
        client = request.client
        client_ip = client.host if client is not None else "testclient"
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if current_time - times[-1] < self.window
        }
        
        # Check rate limit
        if client_ip in self.requests:
            # Remove old timestamps
            self.requests[client_ip] = [
                t for t in self.requests[client_ip]
                if current_time - t < self.window
            ]
            
            if len(self.requests[client_ip]) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Try again later."
                    }
                )
            
            self.requests[client_ip].append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        response = await call_next(request)
        return response


def setup_cors(app):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_middleware(app):
    """Setup all middleware"""
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add rate limiting (100 requests per minute)
    app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
    
    # Setup CORS
    setup_cors(app)

"""
Simple Rate Limiting Configuration using SlowAPI
"""

import os
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status

# Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url, decode_responses=True)

# Rate limiting configuration from environment variables
LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5/hour")
BOOKING_RATE_LIMIT = os.getenv("BOOKING_RATE_LIMIT", "20/hour")
BROWSING_RATE_LIMIT = os.getenv("BROWSING_RATE_LIMIT", "100/hour")

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_url,
    enabled=True
)

# Custom rate limit exceeded handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    response = HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Rate limit exceeded: {exc.detail}"
    )
    return response

# Rate limit decorators for different endpoint types
def login_rate_limit():
    """Rate limit for login endpoints: configurable via LOGIN_RATE_LIMIT env var"""
    return limiter.limit(LOGIN_RATE_LIMIT)

def booking_rate_limit():
    """Rate limit for booking endpoints: configurable via BOOKING_RATE_LIMIT env var"""
    return limiter.limit(BOOKING_RATE_LIMIT)

def browsing_rate_limit():
    """Rate limit for browsing endpoints: configurable via BROWSING_RATE_LIMIT env var"""
    return limiter.limit(BROWSING_RATE_LIMIT)

# User-specific rate limit decorators
def user_login_rate_limit():
    """Rate limit for user-specific login: configurable via LOGIN_RATE_LIMIT env var"""
    def get_user_id(request: Request):
        # Try to get user ID from JWT token if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from auth import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                return payload.get("sub")  # email as user identifier
            except:
                pass
        return get_remote_address(request)
    
    return limiter.limit(LOGIN_RATE_LIMIT, key_func=get_user_id)

def user_booking_rate_limit():
    """Rate limit for user-specific booking: configurable via BOOKING_RATE_LIMIT env var"""
    def get_user_id(request: Request):
        # Try to get user ID from JWT token if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from auth import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                return payload.get("sub")  # email as user identifier
            except:
                pass
        return get_remote_address(request)
    
    return limiter.limit(BOOKING_RATE_LIMIT, key_func=get_user_id)

def user_browsing_rate_limit():
    """Rate limit for user-specific browsing: configurable via BROWSING_RATE_LIMIT env var"""
    def get_user_id(request: Request):
        # Try to get user ID from JWT token if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from auth import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                return payload.get("sub")  # email as user identifier
            except:
                pass
        return get_remote_address(request)
    
    return limiter.limit(BROWSING_RATE_LIMIT, key_func=get_user_id)

"""
Rate limiting and usage tracking utilities
"""
import time
import redis
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from src.core.logging import structured_logger
from src.core.config import settings

class RateLimiter:
    """Rate limiting implementation using Redis"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.default_limits = {
            "requests_per_minute": 100,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        }

    def is_rate_limited(self, user_id: str, endpoint: str,
                       limits: Optional[Dict[str, int]] = None) -> bool:
        """Check if user is rate limited"""
        if not user_id or user_id == "unknown":
            return False  # Don't rate limit unauthenticated requests

        limits = limits or self.default_limits
        current_time = time.time()

        # Check per-minute limit
        per_minute_key = f"rate_limit:{user_id}:{endpoint}:minute"
        per_minute_count = self._increment_counter(per_minute_key, current_time, 60)
        if per_minute_count > limits.get("requests_per_minute", 100):
            structured_logger.log_rate_limit_event(
                user_id, "per_minute", per_minute_count, limits["requests_per_minute"]
            )
            return True

        # Check per-hour limit
        per_hour_key = f"rate_limit:{user_id}:{endpoint}:hour"
        per_hour_count = self._increment_counter(per_hour_key, current_time, 3600)
        if per_hour_count > limits.get("requests_per_hour", 1000):
            structured_logger.log_rate_limit_event(
                user_id, "per_hour", per_hour_count, limits["requests_per_hour"]
            )
            return True

        # Check per-day limit
        per_day_key = f"rate_limit:{user_id}:{endpoint}:day"
        per_day_count = self._increment_counter(per_day_key, current_time, 86400)
        if per_day_count > limits.get("requests_per_day", 10000):
            structured_logger.log_rate_limit_event(
                user_id, "per_day", per_day_count, limits["requests_per_day"]
            )
            return True

        return False

    def _increment_counter(self, key: str, current_time: float, window_seconds: int) -> int:
        """Increment counter with sliding window"""
        # Remove old entries
        self.redis_client.zremrangebyscore(key, '0', current_time - window_seconds)

        # Add current timestamp
        self.redis_client.zadd(key, {str(current_time): current_time})

        # Set expiration
        self.redis_client.expire(key, window_seconds)

        # Return current count
        return self.redis_client.zcard(key)

    def get_rate_limit_info(self, user_id: str, endpoint: str) -> Dict[str, int]:
        """Get current rate limit information"""
        current_time = time.time()

        info = {
            "user_id": user_id,
            "endpoint": endpoint,
            "per_minute": 0,
            "per_hour": 0,
            "per_day": 0
        }

        # Get counts for each window
        for window, seconds in {"per_minute": 60, "per_hour": 3600, "per_day": 86400}.items():
            key = f"rate_limit:{user_id}:{endpoint}:{window.split('_')[1]}"
            self.redis_client.zremrangebyscore(key, '0', current_time - seconds)
            info[window] = self.redis_client.zcard(key)

        return info

class RateLimitMiddleware:
    """Middleware to enforce rate limiting"""

    def __init__(self, rate_limiter: RateLimiter,
                 endpoint_limits: Optional[Dict[str, Dict[str, int]]] = None):
        self.rate_limiter = rate_limiter
        self.endpoint_limits = endpoint_limits or {}

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        user_id = request.headers.get("X-User-Id", "unknown")
        endpoint = request.url.path

        # Get endpoint-specific limits
        limits = self.endpoint_limits.get(endpoint, None)

        # Check if user is rate limited
        if self.rate_limiter.is_rate_limited(user_id, endpoint, limits):
            structured_logger.log_metric(
                "rate_limit_exceeded",
                1,
                {
                    "user_id": user_id,
                    "endpoint": endpoint
                }
            )

            # Log rate limit event
            structured_logger.log_rate_limit_event(
                user_id, "global", 1, 1
            )

            # Return rate limit exceeded response
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later."
                }
            )

        return await call_next(request)

class UsageTracker:
    """Track user and system usage metrics"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.metrics = {
            "requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "database_queries": 0,
            "api_calls": 0,
            "user_messages": 0,
            "ai_responses": 0
        }

    def track_request(self, user_id: str, status: str = "success") -> None:
        """Track request metrics"""
        self.metrics["requests"] += 1
        if status == "success":
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

        # Track per-user requests
        user_key = f"usage:users:{user_id}"
        self.redis_client.hincrby(user_key, "requests", 1)
        self.redis_client.hincrby(user_key, status, 1)

        # Log usage metric
        structured_logger.log_metric(
            "request_tracking",
            1,
            {
                "user_id": user_id,
                "status": status
            }
        )

    def track_database_query(self, user_id: str, query_type: str = "read") -> None:
        """Track database query metrics"""
        self.metrics["database_queries"] += 1

        user_key = f"usage:users:{user_id}"
        self.redis_client.hincrby(user_key, "database_queries", 1)
        self.redis_client.hincrby(user_key, f"db_{query_type}_queries", 1)

        # Log usage metric
        structured_logger.log_metric(
            "database_query_tracking",
            1,
            {
                "user_id": user_id,
                "query_type": query_type
            }
        )

    def track_api_call(self, endpoint: str, status: str = "success") -> None:
        """Track API call metrics"""
        self.metrics["api_calls"] += 1

        endpoint_key = f"usage:endpoints:{endpoint}"
        self.redis_client.hincrby(endpoint_key, "calls", 1)
        self.redis_client.hincrby(endpoint_key, status, 1)

        # Log usage metric
        structured_logger.log_metric(
            "api_call_tracking",
            1,
            {
                "endpoint": endpoint,
                "status": status
            }
        )

    def track_user_message(self, user_id: str) -> None:
        """Track user message metrics"""
        self.metrics["user_messages"] += 1

        user_key = f"usage:users:{user_id}"
        self.redis_client.hincrby(user_key, "user_messages", 1)

        # Log usage metric
        structured_logger.log_metric(
            "user_message_tracking",
            1,
            {
                "user_id": user_id
            }
        )

    def track_ai_response(self, user_id: str) -> None:
        """Track AI response metrics"""
        self.metrics["ai_responses"] += 1

        user_key = f"usage:users:{user_id}"
        self.redis_client.hincrby(user_key, "ai_responses", 1)

        # Log usage metric
        structured_logger.log_metric(
            "ai_response_tracking",
            1,
            {
                "user_id": user_id
            }
        )

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get aggregated usage statistics"""
        return {
            "total_requests": self.metrics["requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "database_queries": self.metrics["database_queries"],
            "api_calls": self.metrics["api_calls"],
            "user_messages": self.metrics["user_messages"],
            "ai_responses": self.metrics["ai_responses"],
            "users": self.get_user_statistics(),
            "endpoints": self.get_endpoint_statistics()
        }

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user-specific usage statistics"""
        users = self.redis_client.keys("usage:users:*")
        user_stats = {}

        for user_key in users:
            user_id = user_key.decode().split(":")[2]
            user_stats[user_id] = {
                k.decode(): int(v) for k, v in self.redis_client.hgetall(user_key).items()
            }

        return user_stats

    def get_endpoint_statistics(self) -> Dict[str, Any]:
        """Get endpoint-specific usage statistics"""
        endpoints = self.redis_client.keys("usage:endpoints:*")
        endpoint_stats = {}

        for endpoint_key in endpoints:
            endpoint = endpoint_key.decode().split(":")[2]
            endpoint_stats[endpoint] = {
                k.decode(): int(v) for k, v in self.redis_client.hgetall(endpoint_key).items()
            }

        return endpoint_stats

# Global rate limiter and usage tracker
rate_limiter = RateLimiter()
usage_tracker = UsageTracker()
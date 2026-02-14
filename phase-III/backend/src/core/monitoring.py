"""
Performance monitoring middleware for API endpoints
"""
import time
from typing import Callable, Awaitable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from src.core.logging import structured_logger
from src.utils.performance import measure_execution_time

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance and collect metrics"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Process request and measure performance"""
        start_time = time.time()
        user_id = request.headers.get("X-User-Id", "unknown")

        # Log incoming request
        structured_logger.log_request(request, user_id=user_id)

        try:
            # Process the request
            response = await call_next(request)
        except Exception as e:
            # Log error with context
            structured_logger.log_error(e, request, user_id=user_id)
            raise
        finally:
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000

            # Log response with performance metrics
            structured_logger.log_response(response, request, processing_time_ms)

            # Log performance metrics
            self.log_performance_metrics(request, response, processing_time_ms, user_id)

        return response

    def log_performance_metrics(self, request: Request, response: Response,
                               processing_time_ms: float, user_id: str) -> None:
        """Log various performance metrics"""
        # Log request processing time
        structured_logger.log_metric(
            "request_processing_time",
            processing_time_ms,
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "user_id": user_id
            }
        )

        # Log database query performance (to be implemented in services)
        structured_logger.log_metric(
            "database_query_performance",
            0.0,  # Will be updated by database query monitoring
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "user_id": user_id
            }
        )

        # Log response size
        response_size = len(response.body or b"") if response.body else 0
        structured_logger.log_metric(
            "response_size",
            response_size,
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "user_id": user_id
            }
        )

        # Log rate limit metrics (to be implemented in rate limiting)
        structured_logger.log_metric(
            "rate_limit_metrics",
            0.0,  # Will be updated by rate limiting
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "user_id": user_id
            }
        )

# Global middleware instance
performance_monitoring_middleware = PerformanceMonitoringMiddleware()
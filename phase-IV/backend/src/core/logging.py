"""
Structured logging configuration for the AI chat backend
"""
import logging
import logging.config
import os
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, Response
from src.core.config import settings

class StructuredLogger:
    def __init__(self, logger_name: str = "chat_backend"):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.setup_logging()

    def setup_logging(self):
        """Configure structured logging with appropriate formatters and handlers"""
        # Clear existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Set logging level
        log_level = logging.INFO if not settings.DEBUG else logging.DEBUG
        self.logger.setLevel(log_level)

        # Create formatter with structured format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler for production (if specified)
        log_file = os.getenv("LOG_FILE")
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_request(self, request: Request, user_id: Optional[str] = None) -> None:
        """Log incoming request with structured data"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "type": "request",
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                "user_id": user_id
            }
            self.logger.info("Incoming Request", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log request: {str(e)}")

    def log_response(self, response: Response, request: Request, processing_time_ms: float) -> None:
        """Log outgoing response with structured data"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "type": "response",
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
                "processing_time_ms": processing_time_ms,
                "response_size": len(response.body or b""),
                "user_id": response.headers.get("X-User-Id", "unknown")
            }
            self.logger.info("Outgoing Response", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log response: {str(e)}")

    def log_error(self, error: Exception, request: Request, user_id: Optional[str] = None) -> None:
        """Log errors with structured data"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "ERROR",
                "type": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host,
                "user_id": user_id
            }
            self.logger.error("Error Occurred", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log error: {str(e)}")

    def log_database_query(self, query: str, execution_time_ms: float, user_id: Optional[str] = None) -> None:
        """Log database queries with performance metrics"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "type": "database_query",
                "query": query[:200],  # Truncate long queries
                "execution_time_ms": execution_time_ms,
                "user_id": user_id
            }
            self.logger.info("Database Query", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log database query: {str(e)}")

    def log_rate_limit_event(self, user_id: str, limit_type: str, current_count: int, max_limit: int) -> None:
        """Log rate limiting events"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "type": "rate_limit",
                "user_id": user_id,
                "limit_type": limit_type,
                "current_count": current_count,
                "max_limit": max_limit
            }
            self.logger.info("Rate Limit Event", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log rate limit event: {str(e)}")

    def log_health_check(self, status: str, response_time_ms: float) -> None:
        """Log health check events"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "type": "health_check",
                "status": status,
                "response_time_ms": response_time_ms
            }
            self.logger.info("Health Check", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log health check: {str(e)}")

    def log_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Log custom metrics"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "type": "metric",
                "metric_name": metric_name,
                "value": value
            }
            if tags:
                log_data["tags"] = tags
            self.logger.info("Custom Metric", extra=log_data)
        except Exception as e:
            self.logger.error(f"Failed to log metric: {str(e)}")

# Global logger instance
structured_logger = StructuredLogger()


def log_operation(operation: str, **kwargs):
    """
    Log an operation with optional parameters

    Args:
        operation: Name of the operation being logged
        **kwargs: Additional parameters to log
    """
    message = f"{operation}"
    structured_logger.logger.info(message, extra=kwargs)


def log_error(error: str, **kwargs):
    """
    Log an error with optional parameters

    Args:
        error: Description of the error
        **kwargs: Additional parameters to log
    """
    structured_logger.logger.error(error, extra=kwargs)


def log_authorization_decision(user_id: str, resource: str, action: str, allowed: bool, **kwargs):
    """
    Log an authorization decision

    Args:
        user_id: ID of the user requesting access
        resource: Resource being accessed
        action: Action being performed
        allowed: Whether access was granted
        **kwargs: Additional parameters to log
    """
    decision = "ALLOWED" if allowed else "DENIED"
    message = f"AUTHORIZATION_DECISION: user={user_id}, resource={resource}, action={action}, decision={decision}"
    structured_logger.logger.info(message, extra=kwargs)


def log_token_validation_result(event: str, user_id: str = "unknown", is_valid: bool = True, reason: str = "", **kwargs):
    """
    Log a token validation result

    Args:
        event: The event type (CREATED, VALID, INVALID, EXPIRED, etc.)
        user_id: The user ID associated with the token
        is_valid: Whether the token is valid
        reason: Reason for validation result
        **kwargs: Additional parameters to log
    """
    message = f"TOKEN_VALIDATION_RESULT: event={event}, user={user_id}, is_valid={is_valid}, reason={reason}"
    structured_logger.logger.info(message, extra=kwargs)


def log_token_lifecycle_event(event: str, user_id: str, token_type: str = "", **kwargs):
    """
    Log a token lifecycle event

    Args:
        event: Type of event (creation, refresh, expiry, etc.)
        user_id: The user ID associated with the token
        token_type: Type of token
        **kwargs: Additional parameters to log
    """
    message = f"TOKEN_LIFECYCLE_EVENT: event={event}, user={user_id}, type={token_type}"
    structured_logger.logger.info(message, extra=kwargs)
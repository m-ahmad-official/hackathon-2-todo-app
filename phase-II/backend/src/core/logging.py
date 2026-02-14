import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_operation(operation: str, user_id: str = None, task_id: int = None):
    """
    Log an operation with user and task context
    """
    timestamp = datetime.now().isoformat()
    context = f"[{timestamp}] Operation: {operation}"
    if user_id:
        context += f", User: {user_id}"
    if task_id:
        context += f", Task: {task_id}"

    logger.info(context)


def log_error(error: Exception, operation: str):
    """
    Log an error with operation context
    """
    timestamp = datetime.now().isoformat()
    logger.error(f"[{timestamp}] Error in '{operation}': {str(error)}")


def log_authentication_event(event: str, user_id: str = None, ip_address: str = None):
    """
    Log authentication-related events
    """
    timestamp = datetime.now().isoformat()
    context = f"[{timestamp}] Auth Event: {event}"
    if user_id:
        context += f", User: {user_id}"
    if ip_address:
        context += f", IP: {ip_address}"

    logger.info(context)


def log_authorization_decision(action: str, user_id: str, resource: str, granted: bool):
    """
    Log authorization decisions
    """
    timestamp = datetime.now().isoformat()
    decision = "GRANTED" if granted else "DENIED"
    context = f"[{timestamp}] Authorization {decision}: User {user_id} attempted to {action} {resource}"

    logger.info(context)


def log_token_validation_result(token_status: str, user_id: str = None, reason: str = None):
    """
    Log JWT token validation results
    """
    timestamp = datetime.now().isoformat()
    context = f"[{timestamp}] Token Validation: {token_status}"
    if user_id:
        context += f", User: {user_id}"
    if reason:
        context += f", Reason: {reason}"

    logger.info(context)


def log_token_lifecycle_event(event: str, user_id: str = None, token_id: str = None, details: str = None):
    """
    Log token lifecycle events (creation, refresh, expiry, etc.)
    """
    timestamp = datetime.now().isoformat()
    context = f"[{timestamp}] Token Lifecycle: {event}"
    if user_id:
        context += f", User: {user_id}"
    if token_id:
        context += f", Token: {token_id}"
    if details:
        context += f", Details: {details}"

    logger.info(context)


def log_security_event(event: str, user_id: str = None, ip_address: str = None, severity: str = "INFO"):
    """
    Log security-related events
    """
    timestamp = datetime.now().isoformat()
    context = f"[{timestamp}] Security Event [{severity}]: {event}"
    if user_id:
        context += f", User: {user_id}"
    if ip_address:
        context += f", IP: {ip_address}"

    if severity.upper() == "ERROR" or severity.upper() == "CRITICAL":
        logger.error(context)
    else:
        logger.info(context)
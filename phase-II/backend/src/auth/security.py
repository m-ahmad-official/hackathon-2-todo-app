from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from src.core.database import get_session
from src.models.task import Task
from src.core.config import settings
from src.core.logging import log_operation, log_token_validation_result, log_token_lifecycle_event


# JWT token creation and validation functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with the provided data
    """
    to_encode = data.copy()

    # Validate input data for security
    if "user_id" in to_encode:
        user_id = to_encode["user_id"]
        if not isinstance(user_id, str) or len(user_id) == 0 or len(user_id) > 255:
            raise ValueError("Invalid user_id: must be a non-empty string with max 255 characters")

    if "role" in to_encode:
        role = to_encode["role"]
        if role not in ["user", "admin"]:
            # In a real application, you might want to be more flexible with roles
            # For now, we'll only allow "user" and "admin" roles
            log_security_event("INVALID_ROLE_ASSIGNED", user_id=to_encode.get("user_id", "unknown"), severity="ERROR")
            raise ValueError(f"Invalid role: {role}. Only 'user' and 'admin' roles are allowed.")

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=int(settings.JWT_EXPIRATION_DELTA))

    to_encode.update({"exp": expire})

    # Add additional security claims
    to_encode.update({
        "iat": datetime.utcnow(),  # Issued at
        "nbf": datetime.utcnow(),  # Not before (token valid immediately)
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Log token creation
    user_id = data.get("user_id", "unknown")
    log_operation("TOKEN_CREATED", user_id=user_id)
    log_token_validation_result("CREATED", user_id=user_id)

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid
    """
    try:
        # Additional security validation
        if not token or len(token) == 0:
            log_security_event("EMPTY_TOKEN_RECEIVED", severity="ERROR")
            return None

        # Check token format (should have 3 parts separated by dots)
        parts = token.split('.')
        if len(parts) != 3:
            log_security_event("MALFORMED_TOKEN_RECEIVED", severity="ERROR")
            return None

        # Verify the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Additional security checks
        user_id = payload.get("user_id", "unknown")

        # Check that the token has not expired (double-check)
        exp_time = payload.get("exp")
        if exp_time:
            current_time = datetime.utcnow().timestamp()
            if current_time >= exp_time:
                log_token_validation_result("EXPIRED", user_id=user_id, reason="Token expiry time reached")
                return None

        # Log successful validation
        log_token_lifecycle_event("VALID", user_id=user_id)

        return payload
    except JWTError as e:
        log_token_validation_result("INVALID", user_id="unknown", reason=f"JWT Error: {str(e)}")
        log_security_event("TOKEN_VERIFICATION_FAILED", severity="ERROR", details=str(e))
        return None
    except Exception as e:
        log_token_validation_result("INVALID", user_id="unknown", reason=f"Unexpected error: {str(e)}")
        log_security_event("TOKEN_VERIFICATION_ERROR", severity="ERROR", details=str(e))
        return None


def validate_jwt_token(token: str) -> Optional[dict]:
    """
    Validate a JWT token and return the payload if valid.
    This function specifically implements the token validation functionality
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Check if token is expired
        exp_time = payload.get("exp")
        if exp_time:
            current_time = datetime.utcnow().timestamp()
            if current_time >= exp_time:
                user_id = payload.get("user_id", "unknown")
                log_token_validation_result("EXPIRED", user_id=user_id, reason="Token expiry time reached")
                return None

        user_id = payload.get("user_id", "unknown")
        log_token_validation_result("VALID", user_id=user_id)
        return payload
    except JWTError as e:
        log_token_validation_result("INVALID", reason=str(e))
        return None


def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_session)
):
    """
    Get the current user's payload from the JWT token
    """
    if credentials is None:
        log_token_validation_result("MISSING", reason="No authorization token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = validate_jwt_token(token)

    if payload is None:
        user_id = "unknown"
        if credentials:
            # Try to extract user_id from the invalid token for logging purposes
            try:
                temp_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
                user_id = temp_payload.get("user_id", "unknown")
            except:
                pass

        log_token_validation_result("FAILED", user_id=user_id, reason="Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("user_id")
    if user_id is None:
        log_token_validation_result("FAILED", reason="No user_id in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user_id(
    current_user_payload: dict = Depends(get_current_user_payload)
):
    """
    Extract the user ID from the current user's payload
    """
    user_id = current_user_payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def authorize_user_for_task(
    task: Task,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Verify that the current user has access to the specified task
    """
    if task.user_id != current_user_id:
        log_operation("AUTHORIZATION_DENIED", user_id=current_user_id, task_id=task.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    log_operation("AUTHORIZATION_GRANTED", user_id=current_user_id, task_id=task.id)
    return task


def validate_token_not_expired(payload: dict) -> bool:
    """
    Validate that the token has not expired
    """
    exp_time = payload.get("exp")
    if exp_time is None:
        return False

    current_time = datetime.utcnow().timestamp()
    is_valid = current_time < exp_time

    user_id = payload.get("user_id", "unknown")
    if not is_valid:
        log_token_validation_result("EXPIRED_CHECK", user_id=user_id, reason="Token expiry validation failed")
    else:
        log_token_validation_result("NOT_EXPIRED", user_id=user_id)

    return is_valid


def get_user_id_from_token_payload(payload: dict) -> Optional[str]:
    """
    Extract the user ID from the token payload
    """
    user_id = payload.get("user_id")
    if user_id:
        log_operation("USER_ID_EXTRACTED", user_id=user_id)
    return user_id
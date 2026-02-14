from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from src.core.config import settings
from src.auth.security import verify_token, create_access_token


# HTTP Bearer scheme for token authentication
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current user ID from the JWT token in the Authorization header
    """
    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_current_user_payload(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the full user payload from the JWT token in the Authorization header
    """
    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def require_authenticated_user(current_user_id: str = Depends(get_current_user_id)):
    """
    Require an authenticated user for endpoints that need authentication
    but don't necessarily need the user ID
    """
    return current_user_id


def verify_admin_access(current_user_payload: dict = Depends(get_current_user_payload)):
    """
    Verify that the current user has admin access
    """
    role = current_user_payload.get("role", "user")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user_payload


def refresh_access_token(current_user_payload: dict) -> str:
    """
    Generate a new access token based on the current user's payload
    This function can be used to refresh an expired token
    """
    # Remove the expiration time from the payload to create a new token
    user_data = {key: value for key, value in current_user_payload.items() if key != "exp"}

    # Create a new token with fresh expiration
    new_token = create_access_token(data=user_data)
    return new_token


def is_token_expired(payload: dict) -> bool:
    """
    Check if the token in the payload is expired
    """
    exp_time = payload.get("exp")
    if exp_time is None:
        return True

    import time
    current_time = time.time()
    return current_time >= exp_time
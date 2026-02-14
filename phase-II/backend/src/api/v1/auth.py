from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from src.core.database import get_session
from src.auth.security import verify_token, create_access_token
from src.auth.deps import is_token_expired
from src.core.config import settings
from src.auth.user_service import authenticate_user, create_user
from src.models.user import UserCreate
from fastapi.responses import JSONResponse

router = APIRouter()
security = HTTPBearer()


@router.post("/token/refresh", summary="Refresh expired JWT token")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh an expired JWT token by generating a new one based on the user's identity.
    This endpoint allows clients to renew their access tokens without re-authenticating.
    """
    token = credentials.credentials

    # Verify the token (this will succeed for expired tokens if we just want to extract user data)
    # Note: In a real implementation, you'd have a separate refresh token mechanism
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the token is expired
    if not is_token_expired(payload):
        # If the token is not expired, we might want to reject the refresh request
        # Or we could allow refreshing slightly before expiry
        pass  # For now, allow refresh regardless of current expiry status

    # Create a new token with the same user data
    user_data = {key: value for key, value in payload.items() if key != "exp"}
    new_token = create_access_token(data=user_data)

    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": int(settings.JWT_EXPIRATION_DELTA),
    }


@router.get("/token/validate", summary="Validate JWT token")
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate a JWT token without using it for any specific operation.
    Returns user information if token is valid.
    """
    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is expired
    exp_time = payload.get("exp")
    if exp_time:
        import time

        current_time = time.time()
        if current_time >= exp_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return {
        "valid": True,
        "user_id": payload.get("user_id"),
        "role": payload.get("role", "user"),
        "exp": payload.get("exp"),
    }


@router.post("/token/revoke", summary="Revoke JWT token (placeholder)")
async def revoke_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Revoke a JWT token (this is a placeholder implementation).
    In a real system, this would add the token to a blacklist/jti registry.
    """
    # In a real implementation, you would add the token to a blacklist
    # For now, we just return a success message
    return {
        "revoked": True,
        "message": "Token revoked successfully (in a real implementation, this would be added to a blacklist)",
    }


@router.post("/login", summary="Authenticate user and return JWT token")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """
    Authenticate a user with email and password.
    Returns a JWT token upon successful authentication.
    """
    user = authenticate_user(session, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token - ensure user_id is a string for JWT
    access_token = create_access_token(
        data={"user_id": str(user.id), "role": getattr(user, "role", "user")}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }


@router.post("/register", summary="Register a new user")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    session: Session = Depends(get_session),
):
    try:
        user_create = UserCreate(email=email, password=password, name=name)
        user = create_user(session, user_create)

        access_token = create_access_token(
            data={"user_id": str(user.id), "role": getattr(user, "role", "user")}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email, "name": user.name},
        }
    except HTTPException:
        # Re-raise HTTP exceptions (like 409 for duplicate email)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )

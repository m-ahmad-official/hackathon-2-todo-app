from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security.http import HTTPBearer
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request as StarletteRequest
from datetime import datetime
from src.core.config import settings
from src.auth.security import verify_token


class JWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify JWT tokens for protected routes
    """
    def __init__(self, app):
        super().__init__(app)
        self.http_bearer = HTTPBearer(auto_error=False)

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public routes (you can customize this list)
        public_routes = [
            "/",  # Root endpoint (public)
            "/docs", "/redoc", "/openapi.json",  # Swagger/OpenAPI docs
            "/health",  # Health check endpoint
            "/api/v1/login",  # Login endpoint (public)
            "/api/v1/register",  # Registration endpoint (public)
            # Add other public routes as needed
        ]

        # Check if the current path is a public route
        is_public_route = any(request.url.path.startswith(route) for route in public_routes)

        # Also skip authentication for OPTIONS requests (preflight CORS requests)
        if request.method == "OPTIONS" or is_public_route:
            response = await call_next(request)
            return response

        # Extract the authorization header
        auth_header = request.headers.get("Authorization")

        if auth_header is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify the format of the authorization header
        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization scheme must be Bearer",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify the token
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token is expired (double-checking expiration)
        exp_time = payload.get("exp")
        if exp_time:
            current_time = datetime.utcnow().timestamp()
            if current_time >= exp_time:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Add user info to request state for use in endpoints
        request.state.user_id = payload.get("user_id")
        request.state.user_role = payload.get("role", "user")
        request.state.token_payload = payload  # Include full payload for potential refresh logic

        response = await call_next(request)
        return response


# Function to create and configure the middleware
def get_jwt_middleware():
    return JWTMiddleware


# Global instance of the middleware (if needed)
jwt_middleware = get_jwt_middleware()
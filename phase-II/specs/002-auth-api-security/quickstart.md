# Quickstart Guide: Authentication & API Security

**Date**: 2026-02-04
**Feature**: Authentication & API Security
**Branch**: 002-auth-api-security

## Overview
This guide provides instructions for setting up and using the JWT-based authentication system with Better Auth for frontend and FastAPI for backend validation.

## Prerequisites
- Python 3.11+
- Node.js 18+ for frontend (if implementing)
- Access to Better Auth configuration
- Existing backend API from Spec-1 (Task API)

## Setup Instructions

### 1. Environment Configuration
Add the following to your `.env` file:

```env
# JWT Configuration
BETTER_AUTH_SECRET=your-better-auth-secret-key
BETTER_AUTH_PUBLIC_KEY=your-public-key-for-verification
JWT_ALGORITHM=RS256
JWT_EXPIRATION_DELTA=604800  # 7 days in seconds
```

### 2. Install Dependencies
```bash
pip install python-jose[cryptography] python-multipart
```

### 3. Update Backend Structure
Ensure the following files exist in your backend:

- `backend/src/auth/middleware.py` - JWT verification middleware
- `backend/src/auth/security.py` - Security utilities
- `backend/src/auth/deps.py` - Authentication dependencies
- `backend/src/api/v1/auth.py` - Public authentication endpoints

### 4. Configure Authentication Middleware
Add JWT middleware to your main FastAPI application in `backend/src/main.py`:

```python
from src.auth.middleware import jwt_middleware
app.add_middleware(jwt_middleware)
```

## Authentication Flow

### 1. User Login/Signup
- User authenticates through Better Auth on the frontend
- Better Auth issues a JWT token
- Frontend stores the token (securely, e.g., in httpOnly cookie or secure localStorage)

### 2. Making Authenticated Requests
- Frontend includes JWT in Authorization header: `Authorization: Bearer {token}`
- Backend middleware validates the token
- Valid token user context is made available to endpoints
- User can access only their own resources

### 3. Example Request
```bash
# With valid JWT token
curl -X GET http://localhost:8000/api/v1/tasks/user123 \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Protected Endpoints

All existing task endpoints now require authentication:
- `GET /api/v1/tasks/{user_id}` - Get tasks for authenticated user
- `POST /api/v1/tasks/` - Create task for authenticated user
- `PUT /api/v1/tasks/{task_id}` - Update task (user must own task)
- `DELETE /api/v1/tasks/{task_id}` - Delete task (user must own task)
- `PATCH /api/v1/tasks/{task_id}/toggle` - Toggle task (user must own task)

## Testing Authentication

### Unit Tests
Run authentication-specific tests:
```bash
pytest tests/unit/test_auth/
```

### Integration Tests
Test the complete authentication flow:
```bash
pytest tests/integration/test_auth_flow.py
```

### Manual Testing
1. Obtain a valid JWT token from Better Auth
2. Make requests with the token to protected endpoints
3. Verify unauthorized requests return 401
4. Verify users can only access their own data

## Error Responses

- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Valid token but insufficient permissions for resource
- `422 Unprocessable Entity`: Malformed token

## Development Notes

- Tokens are stateless - no server-side session storage
- User data isolation is enforced via JWT validation and user_id checking
- All sensitive operations require valid authentication tokens
- Token expiration is enforced automatically by the validation middleware
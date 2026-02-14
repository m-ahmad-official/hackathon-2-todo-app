# Research Summary: Authentication & API Security

**Date**: 2026-02-04
**Feature**: Authentication & API Security
**Branch**: 002-auth-api-security

## Overview
This research document consolidates findings for implementing JWT-based authentication using Better Auth for the frontend and FastAPI middleware for the backend in the Todo application.

## Decisions Made

### 1. JWT Signing Algorithm and Token Expiry Duration
**Decision**: Use RS256 algorithm with 7-day token expiry
**Rationale**: RS256 provides strong security with asymmetric keys, allowing for secure token verification. 7-day expiry balances security with user experience by reducing frequent re-authentication while minimizing token exposure risk.
**Alternatives considered**:
- HS256 with symmetric key - rejected due to key distribution complexity in distributed systems
- Shorter expiry (1 hour) - rejected as it would require frequent re-authentication
- Longer expiry (30 days) - rejected due to increased security risk window

### 2. Shared Secret Storage (Environment Variable Management)
**Decision**: Store JWT public key in environment variables as BETTER_AUTH_PUBLIC_KEY
**Rationale**: Follows security best practices by keeping sensitive information out of source code. Better Auth typically provides the public key for verification.
**Alternatives considered**:
- Hardcoding in source - rejected for obvious security reasons
- External secrets management - overkill for this project scope
- File-based storage - still requires secure file access controls

### 3. Middleware Implementation for FastAPI JWT Verification
**Decision**: Create custom JWTBearer class extending HTTPBearer for token validation
**Rationale**: Provides clean integration with FastAPI's dependency injection system while allowing custom validation logic for user identification and data isolation.
**Alternatives considered**:
- Third-party libraries like fastapi-jwt-auth - introduces unnecessary dependencies
- Manual decorator approach - less maintainable and doesn't integrate well with FastAPI

### 4. Error Handling for Invalid or Expired Tokens
**Decision**: Return HTTP 401 Unauthorized with descriptive error messages
**Rationale**: Follows HTTP standards and provides clear feedback to clients about authentication failures.
**Alternatives considered**:
- Generic error responses - less helpful for debugging
- Different status codes - violates HTTP standards for auth failures

### 5. Frontend API Client Setup to Attach JWT to All Requests
**Decision**: Configure API client to include Authorization header with "Bearer {token}" for protected endpoints
**Rationale**: Standard approach for JWT transmission that's widely supported and understood.
**Alternatives considered**:
- Custom headers - non-standard and potentially problematic
- URL parameters - security risk as tokens may be logged

## Technology Best Practices Researched

### JWT Best Practices
- Use appropriate algorithms (RS256 preferred over HS256)
- Set reasonable expiration times (7-14 days for refresh tokens, shorter for access tokens)
- Include proper claims (iss, exp, sub, aud)
- Validate all claims properly on the server side

### FastAPI Authentication Best Practices
- Use dependency injection for authentication
- Leverage HTTPBearer for standardized token handling
- Implement proper error responses for auth failures
- Separate public and protected endpoints clearly

### Better Auth Integration
- Configure JWT token issuance with proper claims
- Set up proper callback URLs and CORS settings
- Handle token refresh and rotation appropriately

## Research Conclusion
All unknowns from the technical context have been resolved. The architecture is ready for implementation with clear decisions on JWT configuration, token validation, and secure integration between frontend and backend components. The authentication layer will integrate seamlessly with the existing backend API from Spec-1.
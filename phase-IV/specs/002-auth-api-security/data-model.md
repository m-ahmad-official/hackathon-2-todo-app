# Data Model: Authentication & API Security

**Date**: 2026-02-04
**Feature**: Authentication & API Security
**Branch**: 002-auth-api-security

## Entity: User (Enhanced for Authentication)

### Fields
- **user_id** (String/UUID): Unique user identifier from authentication system
- **email** (String): User's email address (unique)
- **name** (String): User's display name
- **created_at** (DateTime): Account creation timestamp
- **updated_at** (DateTime): Last account update timestamp

### Relationships
- **Tasks**: One user can have multiple tasks (via user_id foreign key)

### Validation Rules
- Email must be valid and unique
- User ID must exist in authentication system
- Name must be between 1-100 characters if provided

## Entity: JWT Token

### Fields
- **token** (String): The JWT token string (not stored, stateless)
- **user_id** (String/UUID): Associated user identifier from token claims
- **exp** (DateTime): Token expiration timestamp
- **iat** (DateTime): Token issued at timestamp
- **aud** (String): Audience claim for token validation
- **sub** (String): Subject claim (typically user identifier)

### Validation Rules
- Token must be properly signed with valid signature
- Token must not be expired (exp > current time)
- Token audience must match expected value
- Token issuer must be trusted

### State Transitions
- **Issued**: When user successfully authenticates
- **Valid**: During the token's lifetime (before expiration)
- **Expired**: After the expiration time
- **Revoked**: When token is invalidated (if using token blacklisting)

## Entity: Authenticated Session (Conceptual - Stateless)

### Fields
- **user_id** (String/UUID): User identifier from JWT claims
- **permissions** (Array<String>): User's access permissions
- **expires_at** (DateTime): Session effective expiration
- **last_activity** (DateTime): Last activity timestamp

### Validation Rules
- Session is valid only if underlying JWT is valid
- Permissions must match user's roles in the system
- Session becomes invalid when JWT expires

## Constraints
- **Token Security**: All tokens must be validated against the shared public key
- **User Isolation**: Tasks can only be accessed by the user who owns them (verified via JWT)
- **Statelessness**: No server-side session storage, relying on JWT for state
- **Expiration Enforcement**: Expired tokens must be rejected
- **Authorization**: All protected endpoints require valid JWT tokens

## Indexes
- Index on user_id for efficient user-specific queries (for data isolation)
- Index on token expiration for efficient validation (if storing revoked tokens)
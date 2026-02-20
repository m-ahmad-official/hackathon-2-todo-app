# Data Model: Frontend Application & Full-Stack Integration

**Date**: 2026-02-04
**Feature**: Frontend Application & Full-Stack Integration
**Branch**: 003-frontend-fullstack-integration

## Entity: User (Frontend Representation)

### Fields
- **user_id** (String): Unique identifier from authentication provider
- **email** (String): User's email address
- **name** (String): User's display name (optional)
- **role** (String): User's role in the system (default: "user")
- **created_at** (DateTime): Account creation timestamp
- **updated_at** (DateTime): Last account update timestamp

### Validation Rules
- Email must be valid and match standard email format
- Name must be between 1-100 characters if provided
- Role must be one of: "user", "admin" (default: "user")

### State Transitions
- **Unauthenticated** → **Authenticating** → **Authenticated** → **Logged Out**

## Entity: Task (Frontend Representation)

### Fields
- **id** (Number/String): Unique identifier for the task
- **title** (String): Task title/description (required, max 255 chars)
- **description** (String): Detailed task description (optional, max 1000 chars)
- **completed** (Boolean): Task completion status, default: false
- **user_id** (String): Foreign key linking to user who owns the task
- **created_at** (DateTime): Timestamp when task was created
- **updated_at** (DateTime): Timestamp when task was last updated

### Validation Rules
- Title must be between 1-255 characters
- Description must be between 0-1000 characters if provided
- user_id must match the authenticated user's ID
- completed status can only be true/false
- created_at and updated_at are managed by the backend

### State Transitions
- **Created**: When task is first created (completed = false by default)
- **Updated**: When task details are modified
- **Completed**: When task completion status is toggled to true
- **Reopened**: When completed task is toggled back to false
- **Deleted**: When task is removed from the system

## Entity: Session (Frontend Representation)

### Fields
- **access_token** (String): JWT token for API authentication
- **refresh_token** (String): Token for refreshing access token (if implemented)
- **expires_at** (DateTime): Expiration time for the access token
- **user** (Object): User object with user information
- **authenticated** (Boolean): Whether the session is currently authenticated

### Validation Rules
- access_token must be a valid JWT token
- expires_at must be in the future
- user object must contain valid user information
- authenticated must match the token validity

### State Transitions
- **Initializing**: When the app starts and checks for existing session
- **Checking**: When verifying token validity
- **Valid**: When token is confirmed valid
- **Expired**: When token has expired and needs refresh
- **Invalid**: When token is invalid and user needs to re-authenticate

## Relationships
- **One User** can have **Many Tasks**
- **One Session** belongs to **One User** (at a time)
- **Tasks** are **Owned** by **One User** (enforced by user_id)

## Constraints
- **Data Isolation**: Frontend only displays tasks belonging to the authenticated user
- **Authentication Required**: All task operations require valid authentication
- **Token Validation**: All API requests include valid JWT token in headers
- **Required Fields**: Title is required for task creation
- **Default Values**: Completed field defaults to false on creation

## Frontend State Management
- **Loading States**: Display appropriate loading indicators for API requests
- **Error States**: Handle API errors with user-friendly messages
- **Optimistic Updates**: Update UI immediately with expected changes, revert on error
- **Cache Management**: Use SWR for intelligent caching and revalidation
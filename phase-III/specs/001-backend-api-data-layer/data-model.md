# Data Model: Backend API & Data Layer

**Date**: 2026-02-04
**Feature**: Backend API & Data Layer
**Branch**: 001-backend-api-data-layer

## Entity: Task

### Fields
- **id** (UUID/Integer): Primary key, auto-generated unique identifier
- **title** (String, required): Task title/description (max 255 chars)
- **description** (String, optional): Detailed task description (max 1000 chars)
- **completed** (Boolean): Task completion status, default: false
- **user_id** (String/UUID, required): Foreign key linking to user who owns the task
- **created_at** (DateTime): Timestamp when task was created, auto-generated
- **updated_at** (DateTime): Timestamp when task was last updated, auto-generated

### Relationships
- **Owner**: Each task belongs to one user (identified by user_id)
- **User**: One user can have multiple tasks

### Validation Rules
- Title must be between 1-255 characters
- Description must be between 0-1000 characters if provided
- user_id must be a valid user identifier
- completed status can only be true/false
- created_at and updated_at are automatically managed by the system

### State Transitions
- **Created**: When task is first created (completed = false by default)
- **Updated**: When task details are modified (title, description)
- **Completed**: When task completion status is toggled to true
- **Reopened**: When completed task is toggled back to false

## Entity: User (Reference Only)

### Fields
- **user_id** (String/UUID): Unique user identifier
- Other fields are managed by authentication system (to be implemented in future spec)

### Validation Rules
- user_id must exist in the system before tasks can be created for that user

## Constraints
- **Data Isolation**: Each task can only be accessed by the user who owns it (enforced by user_id)
- **Referential Integrity**: Task.user_id must reference a valid user
- **Required Fields**: title and user_id are required for task creation
- **Default Values**: completed field defaults to false on creation

## Indexes
- Index on user_id for efficient user-specific queries
- Index on (user_id, completed) for filtered queries
- Index on created_at for chronological sorting
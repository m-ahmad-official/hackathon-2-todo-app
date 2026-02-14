# API Reference: Todo Backend API

## Overview

This document describes the REST API endpoints for the Todo application with JWT-based authentication. All endpoints (except authentication) require a valid JWT token in the Authorization header.

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

Tokens are obtained through the authentication endpoints and are valid for 7 days.

## Base URL

```
http://localhost:8000/api/v1
```

## Common Headers

- `Authorization: Bearer <token>` - Required for all protected endpoints
- `Content-Type: application/json` - Required for POST/PUT/PATCH requests

## Common Error Responses

- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Valid token but insufficient permissions for resource
- `404 Not Found`: Requested resource does not exist
- `422 Unprocessable Entity`: Invalid request data

## Endpoints

### Tasks

#### GET `/tasks/{user_id}`

Get all tasks for a specific user.

**Parameters:**
- `user_id` (path): The ID of the user whose tasks to retrieve (must match authenticated user)

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
- `200 OK`: Array of task objects
- `401`: Unauthorized
- `403`: Forbidden (trying to access another user's tasks)

**Example Request:**
```
GET /api/v1/tasks/user123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "user_id": "user123",
    "created_at": "2026-02-04T05:00:00Z",
    "updated_at": "2026-02-04T05:00:00Z"
  }
]
```

#### POST `/tasks/`

Create a new task.

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "title": "string (required, max 255 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean (optional, default: false)",
  "user_id": "string (will be overridden with authenticated user ID)"
}
```

**Response:**
- `201 Created`: Task created successfully
- `400`: Invalid request data
- `401`: Unauthorized

**Example Request:**
```
POST /api/v1/tasks/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "New task",
  "description": "Task description",
  "completed": false,
  "user_id": "user123"
}
```

**Example Response:**
```json
{
  "id": 2,
  "title": "New task",
  "description": "Task description",
  "completed": false,
  "user_id": "user123",
  "created_at": "2026-02-04T05:00:00Z",
  "updated_at": "2026-02-04T05:00:00Z"
}
```

#### PUT `/tasks/{task_id}`

Update an existing task.

**Parameters:**
- `task_id` (path): The ID of the task to update

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)"
}
```

**Response:**
- `200 OK`: Task updated successfully
- `401`: Unauthorized
- `403`: Forbidden (trying to update another user's task)
- `404`: Task not found

**Example Request:**
```
PUT /api/v1/tasks/2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Updated task",
  "completed": true
}
```

#### PATCH `/tasks/{task_id}/toggle`

Toggle the completion status of a task.

**Parameters:**
- `task_id` (path): The ID of the task to toggle

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
- `200 OK`: Task completion status toggled
- `401`: Unauthorized
- `403`: Forbidden (trying to toggle another user's task)
- `404`: Task not found

**Example Request:**
```
PATCH /api/v1/tasks/2/toggle
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### DELETE `/tasks/{task_id}`

Delete a task.

**Parameters:**
- `task_id` (path): The ID of the task to delete

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
- `204 No Content`: Task deleted successfully
- `401`: Unauthorized
- `403`: Forbidden (trying to delete another user's task)
- `404`: Task not found

**Example Request:**
```
DELETE /api/v1/tasks/2
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Authentication

#### POST `/auth/token/refresh`

Refresh an expired JWT token (not yet implemented in this version).

**Headers:**
- `Authorization: Bearer <expired_token>` (required)

**Response:**
- `200 OK`: New token issued
- `401`: Invalid or expired token

## Data Models

### Task

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| title | string | Task title (max 255 chars) |
| description | string | Task description (max 1000 chars) |
| completed | boolean | Whether the task is completed |
| user_id | string | ID of the user who owns the task |
| created_at | string (date-time) | Creation timestamp |
| updated_at | string (date-time) | Last update timestamp |

## Security

- All API requests (except public endpoints) require a valid JWT token
- User data is isolated - users can only access their own resources
- JWT tokens expire after 7 days and must be refreshed
- All sensitive operations are logged for audit purposes

## Rate Limits

- 1000 requests per hour per IP address
- 100 requests per minute per authenticated user

## Versioning

This is version 1 of the API. Future versions will be released as `/api/v2`, `/api/v3`, etc.
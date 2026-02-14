# Frontend API Integration Guide

## Overview

This document describes how the frontend application integrates with the backend API using JWT authentication. The frontend uses a centralized API client that automatically attaches JWT tokens to all requests and handles authentication errors appropriately.

## API Client Configuration

The frontend uses `ApiClient` class for all API communications:

```typescript
import { apiClient } from '../services/api-client';

// All requests automatically include JWT token from storage
const tasks = await apiClient.get('/tasks/user123');
```

## Authentication Flow

### Token Storage
- JWT tokens are stored in browser's localStorage under the key `'auth_token'`
- Tokens are automatically attached to all requests in the `Authorization: Bearer <token>` header

### Token Validation
- Tokens are validated for expiration before each request
- Expired tokens trigger automatic logout and redirect to sign-in page

## Available API Methods

### GET Requests
```typescript
// Get user's tasks
const response = await apiClient.get<TaskResponse[]>(`/tasks/${userId}`);
```

### POST Requests
```typescript
// Create a new task
const newTask = await apiClient.post<TaskResponse>('/tasks/', taskData);
```

### PUT Requests
```typescript
// Update a task
const updatedTask = await apiClient.put<TaskResponse>(`/tasks/${taskId}`, updateData);
```

### PATCH Requests
```typescript
// Toggle task completion
const toggledTask = await apiClient.patch<TaskResponse>(`/tasks/${taskId}/toggle`);
```

### DELETE Requests
```typescript
// Delete a task
await apiClient.delete(`/tasks/${taskId}`);
```

## Error Handling

The API client handles the following error scenarios:
- `401 Unauthorized`: Invalid or expired token - user is logged out and redirected to sign-in
- Network errors: Appropriate error messages displayed
- Server errors: Logged and appropriate user feedback provided

## Components Integration

### Task Components
- `TaskForm`: Handles task creation and updates
- `TaskList`: Displays user's tasks with proper data isolation
- `TaskItem`: Individual task with update/delete/toggle functionality

### Authentication Components
- `AuthProvider`: Context provider for authentication state
- `SignInForm`: Handles user sign-in
- `SignUpForm`: Handles user registration

## Environment Configuration

Required environment variables:
- `NEXT_PUBLIC_API_BASE_URL`: Base URL for backend API (e.g., `http://localhost:8000`)
- `NEXT_PUBLIC_JWT_EXPIRATION_DELTA`: Token expiration time in seconds (default: 604800 for 7 days)

## Security Features

- User data isolation: Each user can only access their own tasks
- Automatic token validation: Requests with expired tokens are rejected
- Secure token handling: Tokens are stored and transmitted securely
- Authorization checks: All operations verify user permissions

## Testing

Unit tests are available in `tests/unit/`:
- `test_auth/`: Authentication-related tests
- `test_api/`: API client tests
- `test_components/`: Component-specific tests

Integration tests are in `tests/integration/`:
- `test_auth_flow.ts`: Complete authentication flow tests
- `test_task_operations.ts`: Task CRUD operation tests
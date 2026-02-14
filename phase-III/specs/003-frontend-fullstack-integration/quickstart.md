# Quickstart Guide: Frontend Application & Full-Stack Integration

**Date**: 2026-02-04
**Feature**: Frontend Application & Full-Stack Integration
**Branch**: 003-frontend-fullstack-integration

## Overview
This guide provides instructions for setting up and running the Next.js frontend application with Better Auth authentication and integration with the secured FastAPI backend.

## Prerequisites
- Node.js 18+ and npm/yarn/pnpm
- Access to the backend API from Spec-1 (Task API)
- Access to authentication system from Spec-2 (JWT-based auth)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Navigate to Frontend Directory
```bash
cd frontend
```

### 3. Install Dependencies
```bash
npm install
# OR
yarn install
# OR
pnpm install
```

### 4. Configure Environment Variables
Create a `.env.local` file in the frontend directory with the following variables:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-better-auth-secret-key
DATABASE_URL=postgresql://neondb_owner:npg_OobETvcr52mH@ep-purple-rain-ahogvd6j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 5. Run Development Server
```bash
npm run dev
# OR
yarn dev
# OR
pnpm dev
```

The application will be available at `http://localhost:3000`

## Frontend Architecture

### App Router Structure
- `(auth)/sign-in/` - Sign in page
- `(auth)/sign-up/` - Sign up page
- `dashboard/` - Main application dashboard with tasks
- `api/auth/[...nextauth]/` - Better Auth API routes

### Component Organization
- `components/ui/` - Base UI components (buttons, inputs, etc.)
- `components/auth/` - Authentication-related components
- `components/tasks/` - Task management components
- `components/layout/` - Layout components (header, sidebar, footer)

### Service Layer
- `services/api-client.ts` - Centralized API client with JWT handling
- `services/auth-service.ts` - Authentication business logic
- `services/task-service.ts` - Task business logic

## Authentication Flow

### 1. User Registration
- User navigates to `/sign-up`
- User fills registration form
- Better Auth creates account and issues JWT token
- User is redirected to dashboard

### 2. User Login
- User navigates to `/sign-in`
- User enters credentials
- Better Auth validates credentials and issues JWT token
- User is redirected to dashboard

### 3. Protected Routes
- All routes except auth routes require authentication
- Unauthenticated users are redirected to sign-in
- JWT token is automatically attached to API requests

### 4. Task Management
- Authenticated users can create, read, update, delete tasks
- All operations are scoped to the authenticated user
- User can only see and modify their own tasks

## API Integration

### API Client Configuration
The frontend uses a centralized API client that:
- Attaches JWT tokens to all requests automatically
- Handles 401 Unauthorized responses by redirecting to login
- Provides consistent error handling
- Implements caching and revalidation with SWR

### Example API Call
```typescript
import { apiClient } from '@/services/api-client';

// Get user's tasks
const getTasks = async (userId: string) => {
  const response = await apiClient.get(`/tasks/${userId}`);
  return response.data;
};

// Create a new task
const createTask = async (taskData: TaskCreate) => {
  const response = await apiClient.post('/tasks/', taskData);
  return response.data;
};
```

## Testing

### Unit Tests
```bash
npm run test:unit
# OR
yarn test:unit
# OR
pnpm test:unit
```

### Integration Tests
```bash
npm run test:integration
# OR
yarn test:integration
# OR
pnpm test:integration
```

### End-to-End Tests
```bash
npm run test:e2e
# OR
yarn test:e2e
# OR
pnpm test:e2e
```

## Building for Production
```bash
npm run build
# OR
yarn build
# OR
pnpm build
```

## Deployment

### Environment Variables for Production
```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-backend-api.com
BETTER_AUTH_SECRET=production-secret-key
DATABASE_URL=your-production-database-url
```

### Deployment Commands
```bash
# Build the application
npm run build

# Start the production server
npm start
```

## Troubleshooting

### Common Issues
- **401 Unauthorized errors**: Verify JWT token is being sent correctly in request headers
- **Cross-origin errors**: Ensure backend API has proper CORS configuration
- **Authentication not persisting**: Check that cookies/local storage are enabled in the browser
- **Task data not isolated**: Verify that user_id is being correctly validated in API calls

### Debugging Tips
- Enable debug logging in environment variables: `DEBUG=true`
- Check browser developer tools for network errors
- Verify that the backend API is running and accessible
- Confirm JWT token format and expiration in browser storage
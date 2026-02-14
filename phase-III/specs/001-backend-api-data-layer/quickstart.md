# Quickstart Guide: Backend API & Data Layer

**Date**: 2026-02-04
**Feature**: Backend API & Data Layer
**Branch**: 001-backend-api-data-layer

## Overview
This guide provides instructions for setting up and running the FastAPI backend with SQLModel and Neon PostgreSQL for the Todo application.

## Prerequisites
- Python 3.11+
- pip package manager
- Git
- Access to Neon PostgreSQL database

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start the Server
```bash
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Task Management
- `GET /api/v1/tasks/{user_id}` - Get all tasks for a user
- `POST /api/v1/tasks/` - Create a new task (requires user_id in payload)
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `PATCH /api/v1/tasks/{task_id}/toggle` - Toggle task completion status

### Example Requests
```bash
# Create a task
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample task", "description": "Task description", "user_id": "user123"}'

# Get user's tasks
curl -X GET http://localhost:8000/api/v1/tasks/user123

# Update a task
curl -X PUT http://localhost:8000/api/v1/tasks/task-id \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated task", "completed": true}'
```

## Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Run All Tests
```bash
pytest
```

## Development
- Use the `--reload` flag with uvicorn for hot-reloading during development
- All API endpoints follow REST conventions
- Database models are defined using SQLModel
- Environment variables are used for configuration
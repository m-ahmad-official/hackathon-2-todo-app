# MCP Tools Specification

**Feature**: 004-ai-chat-backend
**Date**: 2026-02-08
**Status**: Draft

## Overview

This document defines the Model Context Protocol (MCP) tools that the AI agent uses to perform task management operations. Each tool is a standardized interface with well-defined input and output schemas.

## Tool Interface Standard

All MCP tools follow this pattern:

```python
@mcp.tool()
def tool_name(input: dict, context: dict) -> dict:
    """
    Tool description

    Args:
        input: Validated input parameters (JSON)
        context: Execution context containing user_id, etc.

    Returns:
        dict: Standardized response with success flag and result data
    """
    pass
```

**Standard Response Format**:

```json
{
  "success": true|false,
  "data": any,  // Tool-specific result
  "error": "Error message if success=false"
}
```

## Tool Definitions

### 1. add_task

Create a new task.

**Purpose**: Add a new task to the user's task list with optional description and initial completion status.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Optional task description"
    },
    "completed": {
      "type": "boolean",
      "default": false,
      "description": "Whether task is already completed"
    }
  },
  "required": ["title"]
}
```

**Example Input**:

```json
{
  "title": "Buy groceries",
  "description": "Get milk, eggs, and bread"
}
```

**Output Schema**:

```json
{
  "success": true,
  "data": {
    "task": {
      "id": 123,
      "title": "Buy groceries",
      "description": "Get milk, eggs, and bread",
      "completed": false,
      "created_at": "2026-02-08T12:34:56Z"
    }
  }
}
```

**Error Cases**:
- Validation error (missing title, title too long) → `success: false`
- Database error → `success: false`
- User ID mismatch → `success: false`

---

### 2. list_tasks

Retrieve all tasks for the user.

**Purpose**: Get a complete list of the user's tasks, optionally filtered by completion status.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "completed": {
      "type": "boolean",
      "description": "Filter by completion status (omit for all tasks)"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 100,
      "description": "Maximum number of tasks to return"
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Number of tasks to skip for pagination"
    }
  }
}
```

**Example Input**:

```json
{
  "completed": false,
  "limit": 20
}
```

**Output Schema**:

```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 123,
        "title": "Buy groceries",
        "description": "Get milk, eggs, and bread",
        "completed": false,
        "created_at": "2026-02-08T12:34:56Z"
      }
    ],
    "total": 5,
    "limit": 20,
    "offset": 0
  }
}
```

**Error Cases**:
- Invalid pagination parameters → `success: false`
- Database error → `success: false`

---

### 3. complete_task

Mark a task as completed.

**Purpose**: Update a task's completion status to true.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer",
      "minimum": 1,
      "description": "ID of the task to complete"
    }
  },
  "required": ["task_id"]
}
```

**Example Input**:

```json
{
  "task_id": 123
}
```

**Output Schema**:

```json
{
  "success": true,
  "data": {
    "task": {
      "id": 123,
      "title": "Buy groceries",
      "completed": true,
      "updated_at": "2026-02-08T13:00:00Z"
    },
    "message": "Task 'Buy groceries' marked as complete"
  }
}
```

**Error Cases**:
- Task not found → `success: false`
- Task belongs to different user → `success: false`
- Task already completed → `success: false` (with message "Task already completed")
- Database error → `success: false`

---

### 4. delete_task

Remove a task.

**Purpose**: Permanently delete a task from the database.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer",
      "minimum": 1,
      "description": "ID of the task to delete"
    }
  },
  "required": ["task_id"]
}
```

**Example Input**:

```json
{
  "task_id": 123
}
```

**Output Schema**:

```json
{
  "success": true,
  "data": {
    "deleted_task_id": 123,
    "message": "Task deleted successfully"
  }
}
```

**Error Cases**:
- Task not found → `success: false`
- Task belongs to different user → `success: false`
- Database error → `success: false`

---

### 5. update_task

Modify task details.

**Purpose**: Update a task's title, description, or completion status.

**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer",
      "minimum": 1,
      "description": "ID of the task to update"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "New task title"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "New task description"
    },
    "completed": {
      "type": "boolean",
      "description": "New completion status"
    }
  },
  "required": ["task_id"],
  "minProperties": 2  // task_id + at least one field to update
}
```

**Example Input**:

```json
{
  "task_id": 123,
  "title": "Buy groceries at Walmart",
  "completed": true
}
```

**Output Schema**:

```json
{
  "success": true,
  "data": {
    "task": {
      "id": 123,
      "title": "Buy groceries at Walmart",
      "description": "Get milk, eggs, and bread",
      "completed": true,
      "updated_at": "2026-02-08T13:15:00Z"
    },
    "message": "Task updated successfully"
  }
}
```

**Error Cases**:
- Task not found → `success: false`
- Task belongs to different user → `success: false`
- No update fields provided → `success: false`
- Validation error (title too long, etc.) → `success: false`
- Database error → `success: false`

---

## OpenAI Function Calling Integration

Tools are registered with OpenAI agent using function calling format:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": { ... },
                "required": ["title"]
            }
        }
    },
    # ... other tools
]
```

## Agent Behavior Guidelines

The agent should:
1. Parse user intent from natural language
2. Select appropriate tool based on intent
3. Extract required parameters from user message
4. Validate parameters before tool execution
5. Handle tool results and generate user-friendly responses
6. If parameter missing, ask clarifying question instead of guessing
7. If multiple tools applicable, execute in logical order

## Error Handling

All tool errors are propagated to the agent, which should:
- Translate technical errors into natural language
- Provide actionable guidance to user
- Suggest alternative actions when appropriate
- Never expose stack traces or database details to users

## Testing

Each tool MUST have unit tests covering:
- Successful execution with valid input
- All error cases (not found, unauthorized, validation)
- Parameter validation
- Database interactions (use mocking)

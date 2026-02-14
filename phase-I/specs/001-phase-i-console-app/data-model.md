# Data Model: Phase I - In-Memory Console Todo App

## Entities

### Task
Represents a single item in the todo list.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | int | Unique identifier | Auto-increment, Positive |
| title | str | Description of the task | Non-empty, String |
| is_completed | bool | Completion status | Default: False |

## State Management
- All tasks are stored in a global `tasks` list within the application scope.
- `next_id` counter tracks the ID for the next task to be created.

## Validation Rules
- **Title**: String must be stripped of whitespace. Length > 0.
- **ID**: Must exist in the list for Update/Delete/Complete operations.

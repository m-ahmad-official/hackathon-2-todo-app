# Feature Specification: Phase I - In-Memory Console Todo App

**Feature Branch**: `001-phase-i-console-app`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Phase I Scope: In-memory Python console application, single user, no persistence. Required Features: Add Task, View Task List, Update Task, Delete Task, Mark Task Complete/Incomplete."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and View Tasks (Priority: P1)

As a user, I want to add tasks and see them in a list so that I can keep track of what I need to do during my current session.

**Why this priority**: Fundamental requirement of any todo application. Without adding and viewing, the app has no value.

**Independent Test**: Add three tasks and verify they all appear in the task list with correct titles.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I choose "Add Task" and enter a title, **Then** the task should be stored in memory and a success message shown.
2. **Given** tasks have been added, **When** I choose "View Tasks", **Then** all tasks should be displayed with their ID, title, and completion status.

---

### User Story 2 - Task Completion Management (Priority: P1)

As a user, I want to mark tasks as complete or incomplete so that I can track my progress.

**Why this priority**: Core value proposition of a todo list is tracking what is done versus what remains.

**Independent Test**: Create a task, mark it as complete, verify status in list, then mark it as incomplete and verify again.

**Acceptance Scenarios**:

1. **Given** an incomplete task exists, **When** I choose "Mark Complete" and provide its ID, **Then** the task status should update to "Complete".
2. **Given** a complete task exists, **When** I choose "Mark Incomplete" and provide its ID, **Then** the task status should update to "Incomplete".

---

### User Story 3 - Modify and Remove Tasks (Priority: P2)

As a user, I want to edit task titles or delete tasks I no longer need.

**Why this priority**: Essential for maintaining a list when mistakes are made or plans change.

**Independent Test**: Add a task, update its title, verify change, then delete it and verify it's gone from the list.

**Acceptance Scenarios**:

1. **Given** a task exists, **When** I choose "Update Task", provide its ID, and enter a new title, **Then** the task's title should be updated.
2. **Given** a task exists, **When** I choose "Delete Task" and provide its ID, **Then** the task should be removed from memory.

---

### Edge Cases

- **Empty List**: When "View Tasks" is selected but no tasks exist, a message stating "Task list is empty" should be shown.
- **Invalid ID**: When updating, deleting, or changing status for a non-existent ID, an error message "Task ID not found" should be shown.
- **Empty Title**: When adding or updating a task with an empty string, the system should reject it and ask for a valid title.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store tasks in an in-memory data structure (no disk/DB persistence).
- **FR-002**: System MUST provide a menu-based CLI interface for navigation.
- **FR-003**: System MUST assign a unique numerical ID to each task upon creation.
- **FR-004**: System MUST allow tasks to have two states: "Complete" and "Incomplete" (defaulting to Incomplete).
- **FR-005**: System MUST validate that task titles are not empty or solely whitespace.

### Key Entities *(include if feature involves data)*

- **Task**:
  - `id`: Unique integer.
  - `title`: String (non-empty).
  - `is_completed`: Boolean.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the "Add Task" flow in under 10 seconds.
- **SC-002**: 100% of tasks added are correctly displayed in the list during the same session.
- **SC-003**: System correctly identifies invalid IDs 100% of the time.
- **SC-004**: Zero data persists once the application process is terminated (confirming "no persistence" constraint).

## Assumptions

- One session = one application run.
- IDs can simply increment starting from 1.
- CLI menu will be text-based (e.g., "1. Add Task, 2. View Tasks...").

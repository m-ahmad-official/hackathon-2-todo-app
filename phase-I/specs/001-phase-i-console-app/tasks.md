# Tasks: Phase I - In-Memory Console Todo App

**Input**: Design documents from `/specs/001-phase-i-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Pytest unit tests for the service layer logic.

**Organization**: Tasks are grouped by setup, foundation, and user stories to enable incremental delivery.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and structure.

- [X] T001 Create project structure `src/` and `tests/unit/` at repository root
- [X] T002 [P] Initialize Python environment and `.gitignore` for `__pycache__` and `.pytest_cache`
- [X] T003 Configure `pytest` for the `tests/` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data entities and service architecture.

- [X] T004 Create `Task` model in `src/models.py` with `id`, `title`, and `is_completed` fields
- [X] T005 [P] Create `TodoService` class placeholder in `src/todo_service.py` with an in-memory list
- [X] T006 Implement unique ID generation strategy (incremental counter) in `src/todo_service.py`

**Checkpoint**: Foundation ready - basic data structures exist.

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks and see the full list in the current session.

**Independent Test**: Use CLI to add "Test Task", then list all tasks and confirm "Test Task" appears with ID 1.

### Tests for User Story 1
- [X] T007 [P] [US1] Write unit tests for `add_task` and `get_all_tasks` in `tests/unit/test_todo_service.py`

### Implementation for User Story 1
- [X] T008 [US1] Implement `add_task` logic in `src/todo_service.py` (Title validation included)
- [X] T009 [US1] Implement `get_all_tasks` logic in `src/todo_service.py`
- [X] T010 [US1] Create basic CLI loop and "Add Task" / "View List" options in `src/main.py`
- [X] T011 [US1] Integrate `main.py` with `todo_service.py` methods

**Checkpoint**: MVP Ready - App can add and list tasks.

---

## Phase 4: User Story 2 - Task Completion Management (Priority: P1)

**Goal**: Mark existing tasks as Complete or Incomplete.

**Independent Test**: Add task, mark complete, verify in list, mark incomplete, verify in list.

### Tests for User Story 2
- [X] T012 [P] [US2] Write unit tests for `toggle_completion` in `tests/unit/test_todo_service.py`

### Implementation for User Story 2
- [X] T013 [US2] Implement `toggle_completion` logic in `src/todo_service.py` (Handle missing ID)
- [X] T014 [US2] Add completion options to CLI menu in `src/main.py`

---

## Phase 5: User Story 3 - Modify and Remove Tasks (Priority: P2)

**Goal**: Support editing titles and deleting tasks.

**Independent Test**: Update task title and verify change. Delete task and verify it is removed from list.

### Tests for User Story 3
- [X] T015 [P] [US3] Write unit tests for `update_task` and `delete_task` in `tests/unit/test_todo_service.py`

### Implementation for User Story 3
- [X] T016 [US3] Implement `update_task` (title update) in `src/todo_service.py`
- [X] T017 [US3] Implement `delete_task` (removal from list) in `src/todo_service.py`
- [X] T018 [US3] Add Update and Delete options to CLI menu in `src/main.py`

---

## Phase 6: Polish & Input Validation

**Purpose**: Robust error handling and clean exit.

- [X] T019 Implement numerical choice validation for the main menu in `src/main.py`
- [X] T020 Implement `ValueError` handling for ID inputs (reject non-integers) in `src/main.py`
- [X] T021 [P] Ensure "Exit" option correctly terminates the program flow
- [X] T022 [P] Verify "Empty List" edge case message in `src/main.py`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 & 2**: MUST be complete before any User Story work.
- **Phase 3 (MVP)**: First priority after foundation.
- **Phase 4 & 5**: Can proceed in parallel after Phase 3 is stable.
- **Phase 6**: Final verification and robustness.

### Parallel Opportunities
- Unit tests for different stories (T007, T012, T015) can be written in parallel.
- Refinement (T021, T022) can happen once the core CLI loop is in place.

---

## Implementation Strategy: MVP First

1. Complete Setup + Foundational (T001-T006).
2. Implement **User Story 1** (T007-T011).
3. **STOP and VALIDATE**: Run the console app and manually verify Add/View works.
4. Continue with incrementally adding Completion and Edit/Delete features.

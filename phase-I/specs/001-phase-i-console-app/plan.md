# Implementation Plan: Phase I - In-Memory Console Todo App

**Branch**: `001-phase-i-console-app` | **Date**: 2026-01-01 | **Spec**: [specs/001-phase-i-console-app/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-phase-i-console-app/spec.md`

## Summary
Implementation of a basic Python console application that manages a list of tasks in memory. The app uses a simple CLI menu loop and separates task management logic from user interaction.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: None (Standard Library only)
**Storage**: N/A (Python `list` in memory)
**Testing**: `pytest`
**Target Platform**: CLI (Windows/Linux/macOS)
**Project Type**: Single script
**Performance Goals**: Instant response for all operations
**Constraints**: No persistence, no database, no file storage
**Scale/Scope**: Single user session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **SDD Mandatory**: Does this plan follow Constitution -> Spec -> Plan -> Tasks?
- [x] **Agent behavior**: Does this plan avoid manual human coding or "feature invention"?
- [x] **Phase Governance**: Is this feature strictly within the current phase's scope?
- [x] **Tech Constraints**: Does it use Python? (SQLModel/Neon omitted as they are for later phases)
- [x] **Quality**: Does it follow Clean Architecture and separation of concerns?

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-i-console-app/
├── plan.md              # This file
├── research.md          # Implementation decisions
├── data-model.md        # Task entity definition
├── quickstart.md        # Run instructions
└── tasks.md             # Task list (to be generated)
```

### Source Code (repository root)

```text
src/
├── main.py              # Entry point and CLI loop
├── todo_service.py      # Task management logic (In-memory store)
└── models.py            # Task data class

tests/
├── unit/
│   └── test_todo_service.py
```

**Structure Decision**: Option 1 (Single Project) with clear separation between CLI (main.py) and Service (todo_service.py).

## Implementation Details

### 1. Application Structure
- `main.py`: Contains the `while True` loop, input parsing, and menu display.
- `todo_service.py`: A class or set of functions managing the list of tasks.
- `models.py`: A simple `dataclass` or `class` for `Task`.

### 2. ID Generation
- A persistent variable `_next_id` starting at 1, incremented for every new task.

### 3. CLI Loop
```python
def main():
    while True:
        print_menu()
        choice = input("> ")
        # Dispatch to handlers
```

### 4. Error Handling
- Validate input for numerical selections.
- Handle `ValueError` for invalid ID inputs.
- Show clear error messages for "Task Not Found".

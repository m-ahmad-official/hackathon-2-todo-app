# Research: Phase I - In-Memory Console Todo App

This document outlines the technical decisions and research findings for the Phase I implementation.

## Decision 1: Architecture Pattern
- **Decision**: Separation of Concerns between CLI Logic and Task Management.
- **Rationale**: Although Phase I is a single file console app, structuring it with a clear boundary between the "Database/Store" (in-memory list) and the "UI" (CLI) ensures easier migration to future phases (FastAPI/SQLModel).
- **Alternatives Considered**:
    - Monolithic loop: Rejected as it violates "Quality Principles" in the constitution.

## Decision 2: Data Structure
- **Decision**: Python `List` of `Task` objects (via `class` or `TypedDict`).
- **Rationale**: Simple, efficient for a single-user in-memory session.
- **Alternatives Considered**:
    - `Dictionary` with ID as key: Also viable, but `List` with ID attribute matches the behavior of a standard SQL table better for future alignment.

## Decision 3: ID Generation
- **Decision**: Counter-based incremental integer.
- **Rationale**: Simple, deterministic, and fits the Phase I requirement of unique numerical IDs.
- **Alternatives Considered**:
    - UUIDs: Rejected as too complex for Phase I scope.

## Decision 4: CLI Control Flow
- **Decision**: While-loop with `input()` and a dispatch menu.
- **Rationale**: Standard pattern for console applications. Provides a clear entry/exit point.
- **Alternatives Considered**:
    - Command-line arguments (`argparse`): Rejected as the spec requests a "menu-based" flow.

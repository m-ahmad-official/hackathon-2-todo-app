<!--
# Sync Impact Report
- Version change: 0.0.0 -> 1.0.0
- List of modified principles:
  - PRINCIPLE_1: Spec-Driven Development (SDD) Mandatory
  - PRINCIPLE_2: Agent Behavior Rules
  - PRINCIPLE_3: Phase Governance
  - PRINCIPLE_4: Technology Constraints
  - PRINCIPLE_5: Quality Principles
  - PRINCIPLE_6: (Removed unused placeholder)
- Added sections:
  - Technical Stack
  - Development Workflow
- Removed sections:
  - (Generic placeholders)
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: None.
-->

# Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven Development (SDD) Mandatory
Spec-Driven Development is the non-negotiable foundation of this project. No agent may write a single line of application code without approved specifications and tasks. All engineering work must strictly follow the flow: Constitution → Specifications → Technical Plan → Testable Tasks → Implementation.

### II. Agent Behavior Rules
Agents are the primary executors of this project. Humans provide requirements and high-level architectural approval but do not perform manual coding. Agents must never "invent" features or deviate from approved specifications. Any required refinement or change in direction must occur at the specification level (Spec/Plan) before being implemented in code.

### III. Phase Governance
The project is divided into distinct phases (Phase I through Phase V). Each phase is strictly scoped by its own specification. Future-phase features (e.g., Kafka, Kubernetes, Dapr) must never leak into earlier phases. The architecture may evolve only through explicit updates to the specifications and plans, maintaining a clear path from a simple CLI to a cloud-native microservices architecture.

### IV. Technology Constraints
The project adheres to a specific stack to ensure consistency across phases. Python is the mandatory language for all backend services. SQLModel and FastAPI are the primary libraries for data modeling and API development. Neon DB (PostgreSQL) is the source of truth for persistent data. OpenAI Agents SDK and MCP are the primitives for agentic behavior. Later phases will introduce Docker, Kubernetes, Kafka, and Dapr.

### V. Quality Principles
We prioritize Clean Architecture and a clear separation of concerns. Services must be designed as stateless entities where required to facilitate horizontal scaling. The system must be cloud-native ready from inception, even in its simplest forms. Code quality must be maintained through small, testable increments and comprehensive automated testing.

## Technical Stack

### Backend
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Data Modeling**: SQLModel
- **Database**: Neon DB (PostgreSQL)
- **Agent Framework**: OpenAI Agents SDK, MCP

### Infrastructure (Phase progression)
- **Phase I-II**: Local/Desktop
- **Phase III-V**: Docker, Kubernetes, Kafka, Dapr

### Frontend (Phase III+)
- **Framework**: Next.js

## Development Workflow

### 1. Specification & Planning
Every feature or phase begins with a `spec.md` defining requirements and a `plan.md` defining the technical approach. This is the only stage where "invention" is permitted.

### 2. Task Generation
Plans are broken down into granular, dependency-ordered tasks in `tasks.md`. Tasks must be small enough to be verified independently.

### 3. Implementation
Agents execute tasks one by one. Each task completion should ideally be a single commit. Agents must reference the `tasks.md` and `plan.md` throughout execution.

## Governance

### Amendment Procedure
This constitution is the supreme document of the "Evolution of Todo" project. Amendments require a version bump and an update to the `Sync Impact Report` at the top of this file.

### Compliance
All automated agents and human contributors must verify that their work aligns with these principles. The `plan.md` for every feature must include a "Constitution Check" section.

**Version**: 1.0.0 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-01

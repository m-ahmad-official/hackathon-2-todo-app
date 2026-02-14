---
id: 1
title: Establish Evolution of Todo Global Constitution
stage: constitution
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: anonymous
command: /sp.constitution
labels: [governance, constitution, sdd, roadmap]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
tests:
  - null
---

## Prompt

Create a single global constitution for the entire "Evolution of Todo" project covering Phase I through Phase V.

This constitution must define:

1. Spec-Driven Development as mandatory
- No agent may write code without approved specs and tasks
- All work must follow: Constitution → Specs → Plan → Tasks → Implement

2. Agent Behavior Rules
- No manual coding by humans
- No feature invention
- No deviation from approved specifications
- Refinement must occur at spec level, not code level

3. Phase Governance
- Each phase is strictly scoped by its specification
- Future-phase features must never leak into earlier phases
- Architecture may evolve only through updated specs and plans

4. Technology Constraints
- Python for backend
- Next.js for frontend (later phases)
- FastAPI, SQLModel, Neon DB
- OpenAl Agents SDK, MCP
- Docker, Kubernetes, Kafka, Dapr (later phases)

5. Quality Principles
- Clean architecture
- Stateless services where required
- Clear separation of concerns
- Cloud-native readiness

## Response snapshot

Established the primary "Evolution of Todo" project constitution at v1.0.0. Defined Core Principles for SDD, Agent Behavior, Phase Governance, Tech Stack, and Quality. Updated relevant templates (.specify/templates/plan-template.md) to incorporate mandatory constitution checks.

## Outcome

- ✅ Impact: Established global project governance for all five phases.
- 🧪 Tests: No tests run; artifact-only change.
- 📁 Files: Updated constitution and plan template.
- 🔁 Next prompts: Phase I specification.
- 🧠 Reflection: Successfully mapped user requirements to a structured constitution with versioning and impact reporting.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null

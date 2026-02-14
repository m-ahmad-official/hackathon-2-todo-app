---
id: 003
title: AI Chat Backend Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 004-ai-chat-backend
branch: 004-ai-chat-backend
user: user
command: /sp.plan
labels: [planning, implementation, mcp-tools, ai-agent, stateless-architecture]
links:
  spec: specs/004-ai-chat-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-chat-backend/plan.md
  - specs/004-ai-chat-backend/research.md
  - specs/004-ai-chat-backend/data-model.md
  - specs/004-ai-chat-backend/quickstart.md
  - specs/004-ai-chat-backend/contracts/chat-api.yaml
  - specs/004-ai-chat-backend/contracts/mcp-tools.md
tests:
  - null
---

## Prompt

```text
/sp.plan Spec-4: AI Chat Backend & MCP Tools

Create:
- FastAPI chat endpoint → OpenAI Agent → MCP tools → DB
- Models: Conversation, Message
- MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- Agent behavior: map natural language → MCP tool
- Frontend integration via API contract

Decisions:
- Tool input/output formats
- Conversation persistence
- JWT verification & user scoping

Testing:
- MCP tool unit tests
- Chat endpoint tests
- Stateless conversation validation
- JWT enforcement
- Error handling

Technical:
- Stateless server, context from DB
- Modular code for agent, tools, endpoint
- Follow Spec-Kit Plus workflow
```

## Response snapshot

Generated comprehensive implementation plan for AI Chat Backend & MCP Tools (Feature 004). Created Phase 0 research document and Phase 1 artifacts:

**Phase 0 Research** (`research.md`):
- OpenAI Agents SDK integration with function calling
- MCP SDK usage for standardized tool interface
- Conversation context management (20-message window)
- Message persistence strategy (immediate writes)
- JWT verification & user scoping approach
- Rate limiting strategy (60 req/min sliding window)
- Error handling & conversational responses
- MCP tool input/output formats (JSON Schema)
- API contract design (RESTful endpoints)
- Database schema extensions with migration strategy

**Phase 1 Artifacts**:

1. **Data Model** (`data-model.md`):
   - `Conversation` entity with user_id, timestamps, optional title
   - `Message` entity with conversation FK, sender enum, metadata
   - `Task` entity (existing, unchanged)
   - PostgreSQL schema with indexes and cascade delete
   - Trigger to auto-update conversation.updated_at
   - Query patterns and performance considerations
   - Alembic migration strategy

2. **API Contracts** (`contracts/`):
   - `chat-api.yaml`: Complete OpenAPI 3.0 spec with:
     - POST /api/v1/chat/ (send message)
     - GET /api/v1/conversations/ (list)
     - GET /api/v1/conversations/{id} (retrieve)
     - DELETE /api/v1/conversations/{id} (delete)
     - Full request/response schemas with examples
     - Error responses (400, 401, 403, 404, 429, 500, 503)
   - `mcp-tools.md`: MCP tool specifications for:
     - add_task, list_tasks, complete_task, delete_task, update_task
     - JSON Schema input formats, standardized output format
     - OpenAI function calling integration
     - Agent behavior guidelines

3. **Quickstart Guide** (`quickstart.md`):
   - Step-by-step implementation roadmap
   - Detailed file creation checklist
   - System prompt template for agent
   - Code snippets for each major component
   - Validation checklist (12 items)
   - Troubleshooting guide
   - Performance testing approach

4. **Plan Document** (`plan.md`):
   - Complete technical context (Python 3.11, FastAPI stack)
   - Constitution check: All 6 principles PASS
   - Project structure with all new files mapped
   - Zero complexity violations needing justification

5. **Agent Context Update**:
   - Added technologies: OpenAI Agents SDK, MCP SDK, chat agent module
   - Updated CLAUDE.md with new active technologies
   - Context preserved across markers

**Constitution Compliance**: All 6 core principles satisfied with no violations.

## Outcome

- ✅ Impact: Complete implementation design ready for task generation
- 🧪 Tests: Test strategy defined in quickstart (unit, integration, contract tests)
- 📁 Files: Created 5 design artifacts (research.md, data-model.md, quickstart.md, contracts/chat-api.yaml, contracts/mcp-tools.md) and updated plan.md
- 🔁 Next prompts: Ready for `/sp.tasks` to generate actionable task list
- 🧠 Reflection: Successfully created comprehensive technical design covering all aspects: data models, API contracts, MCP tools, agent integration, testing, and performance. All constitution principles validated.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All constitution gates passed, specs complete
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate tasks with `/sp.tasks` and begin implementation

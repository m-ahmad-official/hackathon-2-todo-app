---
id: 001
title: Constitution Update Phase-III AI Chatbot
stage: constitution
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution, phase-iii, ai-chatbot, mcp-tools, stateless-architecture]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
/sp.constitution

Project: Phase-III – Todo AI Chatbot

Core principles:
- Natural language task management via AI
- Stateless chat architecture with DB-stored conversations
- All operations executed through MCP tools
- Secure, user-scoped interactions via JWT
- Spec-driven development workflow

Key standards:
- Chat endpoint must be stateless
- Conversation and message history stored in database
- All task actions performed via MCP tools
- JWT required for all chat requests
- AI must confirm actions and handle errors gracefully

Constraints:
- Frontend: OpenAI ChatKit
- Backend: FastAPI + OpenAI Agents SDK
- MCP Server: Official MCP SDK
- Database: Neon PostgreSQL (SQLModel)
- Authentication: Better Auth (JWT)
- No server-side session storage
- Environment variables for secrets
- Spec-Kit Plus workflow only

Success criteria:
- Chatbot manages tasks via natural language
- Agent correctly uses MCP tools
- Conversations persist across sessions
- Stateless endpoint works reliably
- All actions scoped to authenticated user
```

## Response snapshot

Updated the project constitution from version 1.0.0 to 2.0.0 for Phase-III – Todo AI Chatbot. The constitution now defines six core principles:

1. **AI-Powered Natural Language Task Management** - Users interact via natural language
2. **Stateless Chat Architecture with Persistent Storage** - No server-side sessions, DB persistence
3. **MCP Tool Integration** - All task operations via MCP tools
4. **User-Scoped Security** - JWT-based authentication and data isolation
5. **Conversational Error Handling** - Graceful error messages in natural language
6. **Spec-Driven Development** - Maintain structured workflow

Technology stack constraints include: Frontend (OpenAI ChatKit), Backend (FastAPI + OpenAI Agents SDK), MCP Server (Official MCP SDK), Database (Neon PostgreSQL + SQLModel), and Authentication (Better Auth with JWT).

Version incremented from 1.0.0 to 2.0.0 (MAJOR bump) due to complete redefinition of principles for the new AI chatbot phase.

## Outcome

- ✅ Impact: Updated constitution from v1.0.0 (Todo Web App) to v2.0.0 (AI Chatbot) with complete principle redefinition
- 🧪 Tests: No tests required for constitution update
- 📁 Files: Modified `.specify/memory/constitution.md`
- 🔁 Next prompts: Ready for `/sp.specify` to create feature specifications
- 🧠 Reflection: Successfully transitioned from traditional web app to AI chatbot architecture while maintaining spec-driven development principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation update)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create first feature spec for chatbot integration

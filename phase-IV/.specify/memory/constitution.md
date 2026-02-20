<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 -> 2.0.0 (Major version bump - new phase with redefined principles and architecture)
Modified principles:
  - Reliability -> AI-Powered Natural Language Task Management
  - Security -> Stateless Chat Architecture with Persistent Storage
  - Usability -> MCP Tool Integration
  - Maintainability -> User-Scoped Security
  - Spec-Driven Development -> Spec-Driven Development (retained, enhanced)
  - API Standards -> Conversational Error Handling (new focus)
Added sections: None
Removed sections: None (all sections redefined for Phase-III)
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (no changes required - generic enough)
  ✅ .specify/templates/spec-template.md (no changes required - generic enough)
  ✅ .specify/templates/tasks-template.md (no changes required - generic enough)
Follow-up TODOs: None
-->
# Phase-III – Todo AI Chatbot Constitution

## Core Principles

### AI-Powered Natural Language Task Management
Users interact with the system using natural language to create, update, and manage tasks.
- The chatbot MUST understand and execute task management commands via natural language
- All task operations (CRUD, completion toggle) MUST be accessible through conversational AI
- The AI agent MUST interpret user intent accurately and execute appropriate actions
- Task management MUST feel intuitive and require no technical knowledge from users

**Rationale**: Natural language interfaces dramatically improve user experience and accessibility, making task management effortless.

### Stateless Chat Architecture with Persistent Storage
Chat endpoints maintain no server-side session state; all conversation context is persisted in the database.
- Chat endpoints MUST be stateless with no server-side session storage
- Conversation history and messages MUST be stored in the database for persistence
- Each request MUST contain all necessary authentication context via JWT
- Conversations MUST persist across sessions and be retrievable by authenticated users

**Rationale**: Stateless architecture ensures scalability, reliability, and enables horizontal scaling while database persistence maintains conversation continuity.

### MCP Tool Integration
All task operations are executed through Model Context Protocol (MCP) tools, not direct database calls from the chat endpoint.
- All task actions MUST be performed via MCP tools
- The AI agent MUST use MCP tools to interact with the task management system
- MCP tools MUST encapsulate all business logic and data access patterns
- Direct database access from chat endpoints is prohibited

**Rationale**: MCP tools provide a standardized, maintainable interface for AI agents to interact with backend systems, ensuring consistency and separation of concerns.

### User-Scoped Security
All interactions and data access are strictly scoped to the authenticated user via JWT tokens.
- JWT authentication MUST be enforced for all chat requests
- Users can ONLY access their own conversations, messages, and tasks
- All database queries MUST filter by authenticated user ID
- Security context MUST be propagated through MCP tool calls

**Rationale**: Multi-tenant security is non-negotiable; JWT-based user scoping ensures complete data isolation between users.

### Conversational Error Handling
The AI agent must handle errors gracefully and communicate issues clearly to users through natural language.
- The AI MUST confirm all successful actions with user-friendly messages
- Errors MUST be caught and translated into helpful conversational responses
- The system MUST handle edge cases (e.g., task not found) without technical jargon
- Failed operations MUST provide guidance on how users can correct issues

**Rationale**: Users should never see technical error messages; the AI serves as a friendly interface that translates system state into helpful guidance.

### Spec-Driven Development
All implementations follow the Agentic Dev Stack workflow (Spec → Plan → Tasks → Implementation).
- All development MUST follow the prescribed workflow: Specification → Planning → Task breakdown → Implementation
- Manual coding outside the Spec-Kit Plus workflow is prohibited
- All changes MUST be traceable through the agentic development process
- Commit history MUST reflect the iterative nature of spec-driven development

**Rationale**: Structured, spec-driven development ensures quality, traceability, and maintains alignment with requirements throughout the development lifecycle.

## Key Standards

- Chat endpoint MUST be stateless with no server-side session storage
- Conversation and message history MUST be stored in the database
- All task actions MUST be performed via MCP tools
- JWT authentication MUST be required for all chat requests
- AI agent MUST confirm actions and handle errors gracefully through natural language
- All interactions MUST be scoped to the authenticated user
- Environment variables MUST be used for all secrets (API keys, database credentials)

## Constraints

- **Frontend**: OpenAI ChatKit (or equivalent conversational UI framework)
- **Backend**: Python FastAPI + OpenAI Agents SDK
- **MCP Server**: Official MCP SDK (Python)
- **Database**: Neon PostgreSQL with SQLModel ORM
- **Authentication**: Better Auth with JWT tokens
- **Architecture**: No server-side session storage; stateless chat endpoints
- **Security**: Environment variables for all secrets; never hardcode credentials
- **Workflow**: Spec-Kit Plus workflow only (no direct manual coding)

## Success Criteria

- Chatbot successfully manages tasks via natural language commands
- AI agent correctly uses MCP tools for all task operations
- Conversations persist across user sessions and are retrievable
- Stateless endpoint works reliably under load
- All actions are strictly scoped to the authenticated user
- Error messages are user-friendly and actionable
- Complete traceability from specification through implementation

## Governance

- This constitution supersedes all other development practices and guidelines
- All code reviews MUST verify compliance with these principles and constraints
- Any deviation from these principles requires explicit approval and documentation
- Amendments to this constitution require formal proposal, discussion, and approval process
- Use Spec-Kit Plus tools and Claude Code for all development activities

**Version**: 2.0.0 | **Ratified**: 2026-02-08 | **Last Amended**: 2026-02-08

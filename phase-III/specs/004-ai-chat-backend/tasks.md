# Tasks: AI Chat Backend & MCP Tools

**Input**: Design documents from `/specs/004-ai-chat-backend/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, quickstart.md

> **IMPORTANT**: Tasks are organized by user story to enable independent implementation and testing of each story. Each phase should deliver a working increment that can be demonstrated.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for new modules

- [X] T001 Create directory structure for new modules
  - `backend/src/models/conversation.py` and `backend/src/models/message.py`
  - `backend/src/mcp/` and `backend/src/mcp/tools/`
  - `backend/src/agent/`
  - `backend/src/services/conversation_service.py`
  - `backend/tests/unit/test_mcp_tools.py`
  - `backend/tests/unit/test_conversation_service.py`
  - `backend/tests/integration/test_chat_flow.py`
  - `backend/tests/integration/test_mcp_tools.py`

- [X] T002 Verify dependencies in `requirements.txt` include OpenAI Agents SDK and MCP SDK
  - Check for `openai-agents`, `mcp`, `python-jose[cryptography]`
  - Add missing dependencies and run `pip install -r requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Create Alembic migration for conversations and messages tables
  - Run `alembic revision --autogenerate -m "Add conversations and messages tables"`
  - Review and adjust migration if needed
  - File: `alembic/versions/xxx_add_conversations_messages.py`
  - Run `alembic upgrade head` to apply migration

- [X] T004 [P] Implement Conversation and Message SQLModel classes
  - `backend/src/models/conversation.py`: Conversation model with user_id, timestamps, title
  - `backend/src/models/message.py`: Message model with FK to conversation, sender enum, metadata
  - Include appropriate field constraints (max_length, indexes)
  - Add relationship definitions

- [X] T005 Implement conversation service layer (`backend/src/services/conversation_service.py`)
  - `create_conversation(user_id: str) -> Conversation`
  - `get_conversation(conversation_id: int, user_id: str) -> Conversation` (with ownership check)
  - `list_conversations(user_id: str, limit: int, offset: int) -> List[Conversation]`
  - `delete_conversation(conversation_id: int, user_id: str)`
  - `add_message(conversation_id: int, content: str, sender: str, metadata: dict = None) -> Message`
  - `get_conversation_messages(conversation_id: int, limit: int = 20) -> List[Message]`
  - `get_recent_messages(conversation_id: int, limit: int = 20) -> List[Message]` (for context)

- [X] T006 Implement MCP tools (`backend/src/mcp/tools/`)
  - `add_task.py`: Create task tool
  - `list_tasks.py`: List tasks with optional filters
  - `complete_task.py`: Mark task complete
  - `delete_task.py`: Delete task
  - `update_task.py`: Update task fields
  - Each tool must: accept JSON input, validate parameters, enforce user_id from context, call task_service, return standardized response

- [X] T007 Implement MCP server setup (`backend/src/mcp/server.py`)
  - Initialize MCP server instance
  - Register all tools from `mcp.tools` package
  - Configure server to run within FastAPI lifecycle or as standalone

- [X] T008 [P] Implement OpenAI agent setup (`backend/src/agent/`)
  - `chat_agent.py`: Initialize OpenAI agent with system prompt, register MCP tools via function calling
  - `context_builder.py`: Function to load recent messages from database and format for OpenAI
  - System prompt should follow template from quickstart.md with task management guidelines
  - Agent should be stateless - accepts context as input, returns response

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Chat Message and Manage Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to send natural language messages and have the AI agent create, view, complete, and delete tasks through conversation.

**Independent Test**: Can be fully tested by sending a chat message via the API endpoint and receiving a structured response confirming the action taken. The response should include the updated task state.

### Tests for User Story 1 (OPTIONAL - only if tests requested)

> **NOTE**: The spec did NOT explicitly request tests, but best practice is to include them. **Tests are OPTIONAL** - delete this subsection if not implementing tests.

- [ ] T009 [P] [US1] Contract test for chat endpoint in `backend/tests/contract/test_chat_api.py`
  - Test POST /api/v1/chat/ with valid JWT and message
  - Verify response format matches `contracts/chat-api.yaml`
  - Test new conversation creation (no conversation_id)
  - Test continuing existing conversation (with conversation_id)
  - Test authentication required (401 without token)
  - Test rate limiting (429 after limit)

- [ ] T010 [P] [US1] Integration test for full chat flow in `backend/tests/integration/test_chat_flow.py`
  - Test: User sends "Add task X" → task created → response includes task confirmation
  - Test: User sends "Show my tasks" → list returned correctly
  - Test: User sends "Complete task 1" → task marked complete
  - Test: User sends "Delete task 1" → task removed
  - Use test database with fixtures

### Implementation for User Story 1

- [X] T011 [P] [US1] Implement FastAPI chat endpoint in `backend/src/api/v1/chat.py`
  - `POST /api/v1/chat/` endpoint
  - Parse request body (ChatRequest: message, optional conversation_id)
  - Extract JWT → user_id
  - Apply rate limiting middleware (60 req/min per user - configure if not already in main.py)
  - If conversation_id provided: verify ownership, load conversation; else: create new conversation
  - Save user message to database via conversation_service.add_message()
  - Load recent context (last 20 messages) via conversation_service.get_recent_messages()
  - Call chat_agent.process_message(message, context, user_id)
  - Agent returns AI response text + list of tool calls executed
  - Save AI response message to database
  - Return ChatResponse with conversation_id, message, and context metadata (tasks_modified, action_taken)
  - Error handling: catch exceptions, log, return user-friendly error

- [X] T012 [P] [US1] Implement chat orchestration service (`backend/src/services/chat_service.py`)
  - `process_chat_message(user_id: str, conversation_id: Optional[int], message: str) -> ChatResponse`
  - Orchestrates: conversation lookup/creation, message persistence, context building, agent invocation, tool execution, response formatting
  - This is the main business logic coordinator for user story 1

- [X] T013 [US1] Register chat routes in main FastAPI app
  - Import chat router from `api.v1.chat`
  - Include router in main.py with prefix `/api/v1`
  - Ensure JWT dependency applied (use existing `get_current_user` from auth)

**Checkpoint**: User Story 1 should be fully functional - users can send chat messages and manage tasks through natural language

---

## Phase 4: User Story 2 - Conversation Persistence Across Sessions (Priority: P2)

**Goal**: Ensure conversations and messages are persisted and retrievable across user sessions.

**Independent Test**: Can be tested by sending messages, logging out, logging back in, and retrieving the same conversation with all messages intact.

### Implementation for User Story 2

- [X] T014 [P] [US2] Implement GET `/api/v1/conversations/` endpoint in `backend/src/api/v1/chat.py`
  - Query user's conversations via conversation_service.list_conversations()
  - Support pagination: query params `limit` (default 20), `offset` (default 0)
  - Return ConversationListResponse with conversations array containing id, created_at, updated_at, message_count, last_message preview
  - Ensure user_id from JWT used to filter conversations

- [X] T015 [US2] Implement GET `/api/v1/conversations/{conversation_id}` endpoint
  - Retrieve conversation with all messages
  - Call conversation_service.get_conversation(conversation_id, user_id) - must verify ownership
  - Return ConversationDetailResponse with messages in chronological order
  - Return 404 if conversation not found, 403 if wrong user

- [X] T016 [US2] Implement DELETE `/api/v1/conversations/{conversation_id}` endpoint
  - Delete conversation and all associated messages (ON DELETE CASCADE should handle)
  - Call conversation_service.delete_conversation(conversation_id, user_id)
  - Return 204 on success, 404 if not found, 403 if wrong user

- [X] T017 [P] Add conversation title auto-generation logic (optional but helpful)
  - Extract title from first user message or AI response
  - Update conversation.title in conversation_service.create_conversation()
  - Allow manual title updates in future (out of scope for MVP)

**Checkpoint**: User Stories 1 AND 2 should both work independently - users can chat and retrieve conversation history

---

## Phase 5: User Story 3 - Multi-Turn Conversations with Context (Priority: P3)

**Goal**: AI remembers context from previous messages in a conversation for natural, flowing interactions.

**Independent Test**: Can be tested by sending a series of related messages (e.g., "Create a task X" followed by "Mark it as high priority") and verifying the AI understands context without explicit references.

### Implementation for User Story 3

- [X] T018 [P] [US3] Enhance context builder to include full conversation history
  - In `backend/src/agent/context_builder.py`: Load last 20 messages from database
  - Format messages as OpenAI API format: `{"role": "user"|"assistant", "content": "..."}`
  - Ensure chronological order (oldest first)
  - Insert system message at beginning (from agent system prompt)

- [X] T019 [US3] Update chat agent to handle context effectively
  - In `backend/src/agent/chat_agent.py`: ensure agent receives full context with each request
  - Agent should maintain no internal state - context passed each time
  - Verify agent uses context to resolve references like "it", "that task", etc.
  - May need to improve system prompt to instruct agent on context usage

- [X] T020 [P] [US3] Implement token tracking and context window management
  - Count tokens in conversation history (use tiktoken or simple approximation)
  - If approaching model's context limit (e.g., 8k tokens), implement summarization or truncation
  - For MVP: simple truncate to last N messages (already planned as 20)
  - Log token counts for monitoring

**Checkpoint**: All user stories (1, 2, 3) should now work - conversations retain context naturally

---

## Phase 6: User Story 4 - User-Scoped Data Isolation (Priority: P4)

**Goal**: Verify and validate that all data access is properly scoped to authenticated users.

**Independent Test**: Can be tested by creating data as one user and attempting to access as another user - access should be denied.

### Implementation for User Story 4

- [X] T021 [P] [US4] Audit all database queries for user scoping
  - Review conversation_service.py: all queries must include `WHERE user_id = :user_id`
  - Review mcp tools: ensure user_id extracted from context and passed to task_service
  - Review chat endpoint: JWT verification before any data access
  - Document any missing scoping and fix

- [X] T022 [US4] Add explicit ownership checks to sensitive operations
  - In conversation_service.get_conversation(): verify `conversation.user_id == user_id`
  - In conversation_service.delete_conversation(): verify ownership
  - In MCP tools: ensure `task.user_id == user_id` before operations
  - Raise HTTPException with 403 if ownership fails

- [X] T023 [US4] Implement security logging
  - Log all access attempts to conversations (including denied attempts)
  - Include user_id, conversation_id, action, timestamp
  - Use backend's existing logging configuration

- [ ] T024 [US4] Add rate limiting enforcement to chat endpoint
  - If not already done in T011, implement rate limiting middleware
  - Use existing rate limiter from `backend/src/core/rate_limiting.py` or implement simple in-memory version
  - 60 requests per minute per user_id
  - Return 429 with appropriate headers when limit exceeded
  - **NOTE**: RateLimiter class exists with Redis backend. For MVP, recommend simple in-memory fallback or document Redis requirement.

**Checkpoint**: All user stories complete - system is secure and production-ready

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T025 [P] Error handling refinement
  - Review all exception handlers in chat endpoint
  - Ensure errors are translated to user-friendly messages (per US4 requirements)
  - Log technical details but return generic messages to users
  - Handle specific cases: OpenAI API errors, database errors, validation errors, MCP tool failures

- [ ] T026 [P] Comprehensive testing (if not done in earlier phases)
  - Unit tests for all MCP tools (add, list, complete, delete, update) - coverage >80%
  - Unit tests for conversation_service functions
  - Integration test for full chat flow: user message → AI → tool execution → response
  - Contract tests to verify API responses match openapi spec
  - Security tests: verify user scoping, JWT enforcement

- [ ] T027 [P] API documentation update
  - Update `backend/docs/api-reference.md` with chat endpoints
  - Include example requests/responses from `contracts/chat-api.yaml`
  - Document authentication requirements, rate limits, error responses
  - Provide curl examples for testing

- [ ] T028 [P] Performance optimization
  - Add database indexes if queries are slow (should already be in migration)
  - Optimize context loading query (use indexed queries, limit to 20 messages)
  - Consider adding caching for frequently accessed conversations (optional)
  - Ensure chat agent initializes efficiently (don't recreate on every request)

- [ ] T029 [P] Configuration management
  - Verify OPENAI_API_KEY in .env (not committed)
  - Set OPENAI_MODEL=gpt-4 in config
  - Review .env.example and document all required variables
  - Ensure rate limit configuration is adjustable

- [ ] T030 [P] Run quickstart validation and fix any issues
  - Follow quickstart.md validation checklist
  - Test all acceptance scenarios from spec
  - Verify success criteria can be measured
  - Document any deviations

- [ ] T031 [P] Create demo/usage documentation for frontend integration
  - Document API contract for frontend team (Spec-5)
  - Provide example code for chatApi.ts
  - Note authentication requirement (JWT token)
  - Describe error handling patterns

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in priority order: US1 → US2 → US3 → US4
  - Each builds on previous: US2 needs US1, US3 needs US2, US4 validates all
  - They could technically be parallel after foundation, but sequential makes sense
- **Polish (Phase 7)**: Depends on all user stories being complete

### Within Each User Story

- Tests (if included) should be created BEFORE implementation tasks (TDD approach)
- Models → Services → Endpoints → Integration (logical order)
- Core chat flow (T011-T013) is the MVP and should be completed first

### Parallel Opportunities

- **Setup phase**: T001 and T002 are independent, can run in parallel
- **Foundational phase**: All [P] marked tasks can run in parallel:
  - T003 (migration), T004 (models), T005 (conversation service), T006 (MCP tools), T007 (MCP server), T008 (agent setup) are all independent
  - These can all be worked on simultaneously to accelerate foundation
- **User Story 1**: T011, T012, T013 are dependent (endpoint needs service, service needs agent) - must be sequential
- **User Story 2**: T014, T015, T016 are mostly independent but logically ordered (list before get, get before delete)
- **User Story 3**: T018, T019, T020 have dependencies (context builder before agent update, token tracking optional)
- **User Story 4**: T021-T024 should be sequential (audit → fix issues → add logging → rate limiting)
- **Polish**: Most tasks [P] can run in parallel after stories complete

### Parallel Execution Example: Foundational Phase

```bash
# Launch all parallel foundational tasks together:
Task: T003 Create database migration (alembic)
Task: T004 Implement Conversation/Message models
Task: T005 Implement conversation_service.py
Task: T006 Implement all 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
Task: T007 Implement MCP server setup
Task: T008 Implement OpenAI agent and context builder
# All these can be done in parallel since they touch different files
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (T011-T013)
4. **STOP and VALIDATE**: Test User Story 1 independently - can send message, AI creates task, response received
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add Polish tasks → Release candidate

Each story adds value:
- US1: Core task management via chat
- US2: Conversations persist and can be reviewed
- US3: AI understands context, conversations feel natural
- US4: System is secure and validated

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (all parallel)
2. Once Foundation done:
   - Developer A: User Story 1 (chat endpoint, service, agent integration)
   - Developer B: User Story 2 (conversation list/detail/delete endpoints)
   - Developer C: User Story 3 (context enhancement, token tracking)
3. Stories complete and integrate independently
4. Team focuses on Polish together

---

## Notes

- [P] tasks = different files, no dependencies on each other within same phase
- [USx] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Foundation phase (Phase 2) is blocking - all must be done before any story works
- Tests are OPTIONAL - included based on best practices but can be removed if truly not needed
- FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK are the core technologies from constitution

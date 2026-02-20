# Quickstart: AI Chat Backend & MCP Tools

**Feature**: 004-ai-chat-backend
**Date**: 2026-02-08
**Status**: Draft

## Prerequisites

Before starting implementation, ensure you have:

1. Open `<project-root>/backend/.env` and configure:
   ```bash
   OPENAI_API_KEY=sk-your-openai-api-key
   OPENAI_MODEL=gpt-4
   ```

2. Verify database migrations are up to date:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. Ensure backend server is running:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Implementation Overview

This feature adds three major components:

1. **Chat API**: Stateless endpoint for AI-powered task management
2. **MCP Server**: Tool interface for task operations
3. **Agent Integration**: OpenAI agent that uses tools via MCP

## Step-by-Step Implementation

### Step 1: Database Models

Add new models for conversations and messages.

**Files to create**:
- `backend/src/models/conversation.py`
- `backend/src/models/message.py`

**Key tasks**:
- Define `Conversation` model with `user_id`, timestamps
- Define `Message` model with foreign key to conversation
- Both inherit from `SQLModel`
- Add appropriate indexes for performance

### Step 2: Database Migration

Create Alembic migration to add new tables:

```bash
cd backend
alembic revision --autogenerate -m "Add conversations and messages tables"
alembic upgrade head
```

**Expected changes**:
- `conversation` table with id, user_id, created_at, updated_at, title
- `message` table with id, conversation_id, content, sender, created_at, metadata
- Foreign key constraints and indexes
- Trigger to update `conversation.updated_at` on new message

### Step 3: MCP Tools Implementation

Create MCP server with task management tools.

**Files to create**:
- `backend/src/mcp/__init__.py`
- `backend/src/mcp/server.py`
- `backend/src/mcp/tools/__init__.py`
- `backend/src/mcp/tools/add_task.py`
- `backend/src/mcp/tools/list_tasks.py`
- `backend/src/mcp/tools/complete_task.py`
- `backend/src/mcp/tools/delete_task.py`
- `backend/src/mcp/tools/update_task.py`

**Key tasks**:
- Initialize MCP server in `server.py`
- Each tool as separate file with `@mcp.tool()` decorator
- All tools receive `user_id` from context
- Tools call existing `task_service` functions
- Return standardized response format with `success` flag

### Step 4: AI Agent Setup

Configure OpenAI agent with tools and system prompt.

**Files to create**:
- `backend/src/agent/__init__.py`
- `backend/src/agent/chat_agent.py`
- `backend/src/agent/context_builder.py`

**Key tasks**:
- `chat_agent.py`: Initialize OpenAI agent with system prompt defining task management behavior
  - System prompt should instruct agent to help with tasks, be conversational but concise
  - Register all MCP tools as functions
  - Set up conversation state handling (model parameters)
- `context_builder.py`: Function to load recent conversation context from database
  - Query last 20 messages for given conversation_id
  - Format as OpenAI message list (user/ai roles)
  - Return in chronological order
- Agent should be stateless - all context reconstructed per request

**System Prompt Template**:

```
You are a helpful task management assistant. Your job is to help users manage their tasks through natural conversation.

Guidelines:
- Be concise and friendly
- Confirm actions before taking them when ambiguous
- Use the provided tools to create, view, complete, and delete tasks
- Reference previous conversation context when appropriate
- If user asks about something unrelated, politely steer back to task management
- Always provide clear confirmation after performing actions

Available tools: add_task, list_tasks, complete_task, delete_task, update_task
```

### Step 5: Conversation Service

Implement service layer for conversation and message operations.

**Files to create**:
- `backend/src/services/conversation_service.py`

**Key functions**:
- `create_conversation(user_id: str) -> Conversation`: Create new conversation
- `get_conversation(conversation_id: int, user_id: str) -> Conversation`: Get conversation with ownership check
- `list_conversations(user_id: str, limit: int, offset: int) -> List[Conversation]`: Paginated list
- `delete_conversation(conversation_id: int, user_id: str)`: Delete conversation and messages
- `add_message(conversation_id: int, content: str, sender: str, metadata: dict = None) -> Message`: Create message
- `get_conversation_messages(conversation_id: int) -> List[Message]`: Get all messages in chronological order
- `get_recent_messages(conversation_id: int, limit: int = 20) -> List[Message]`: Get last N messages for context

**Important**: All functions must enforce user scoping - users can only access their own data.

### Step 6: Chat Endpoint

Create FastAPI endpoint for chat operations.

**File to create**:
- `backend/src/api/v1/chat.py`

**Endpoints**:
1. `POST /api/v1/chat/` - Send message (main endpoint)
2. `GET /api/v1/conversations/` - List user's conversations
3. `GET /api/v1/conversations/{conversation_id}` - Get conversation with messages
4. `DELETE /api/v1/conversations/{conversation_id}` - Delete conversation

**Implementation notes**:
- `/chat/` endpoint:
  - Parse request body (message, optional conversation_id)
  - Validate JWT from Authorization header → extract user_id
  - Rate limit check: 60 req/min per user_id
  - If conversation_id provided, verify ownership and load conversation
  - Otherwise, create new conversation
  - Save user message to database
  - Load recent message context (last 20 messages) using `context_builder`
  - Call `chat_agent.process_message(user_message, context)`
  - Agent returns tool calls/response
  - Execute MCP tools as called by agent
  - Save AI response to database
  - Return structured response with conversation_id, message, context metadata
- Error handling: Catch exceptions, log details, return user-friendly error message
- Apply rate limiting middleware (already configured in main.py)

**Response format** per `contracts/chat-api.yaml`:
```json
{
  "conversation_id": 42,
  "message": {
    "content": "AI response text",
    "sender": "ai",
    "timestamp": "2026-02-08T12:34:56Z"
  },
  "context": {
    "tasks_modified": [123],
    "action_taken": "Created new task"
  }
}
```

### Step 7: Testing

Implement comprehensive test suite.

**Files to create**:
- `backend/tests/contract/test_chat_api.py`: Contract tests for API endpoints
- `backend/tests/integration/test_chat_flow.py`: End-to-end user scenarios
- `backend/tests/integration/test_mcp_tools.py`: MCP tool integration
- `backend/tests/unit/test_chat_service.py`: Service layer unit tests
- `backend/tests/unit/test_conversation_service.py`: Conversation service unit tests
- `backend/tests/unit/test_mcp_tools.py`: Individual MCP tool tests

**Test coverage goals**:
- Chat endpoint: happy path, validation errors, auth errors, rate limiting
- Conversation service: CRUD operations, user scoping, message retrieval
- MCP tools: All tools with various inputs, error cases
- Integration: Full chat flow from message to task creation
- Edge cases: Long messages, expired JWT, concurrent requests

### Step 8: API Documentation

Update API documentation:

**File to update**:
- `backend/docs/api-reference.md` or create new doc

Add sections for:
- Chat endpoint usage examples
- Authentication requirements
- Rate limiting policy
- Error responses
- Example requests/responses

### Step 9: Frontend API Client

Create frontend service for chat API (for Spec-5 integration).

**File to create**:
- `frontend/src/services/chatApi.ts`

**Key functions**:
- `sendMessage(message: string, conversationId?: number): Promise<ChatResponse>`
- `listConversations(): Promise<ConversationSummary[]>`
- `getConversation(conversationId: number): Promise<ConversationDetail>`
- `deleteConversation(conversationId: number): Promise<void>`

**Implementation notes**:
- Use existing `axios` instance with JWT from auth
- Include `Authorization: Bearer <token>` header
- Proper TypeScript types for request/response
- Error handling with user-friendly messages

### Step 10: Monitoring & Logging

Add logging and monitoring:

**Implementation**:
- Log all chat requests (user_id, conversation_id, timestamp)
- Log MCP tool executions (tool name, parameters, duration)
- Log AI API calls (but not full content for privacy)
- Log errors with stack traces for debugging
- Consider adding metrics: request count, response times, error rates

**Files to modify**:
- `backend/src/services/chat_service.py`: Add structured logging
- `backend/src/mcp/server.py`: Log tool invocations
- `backend/src/agent/chat_agent.py`: Log AI interactions

## Validation Checklist

Before considering feature complete, verify:

- [ ] Database migrations applied successfully
- [ ] MCP tools all have unit tests with >80% coverage
- [ ] Chat endpoint passes contract tests
- [ ] Full integration test covers: user sends message → AI creates task → response returned
- [ ] JWT authentication enforced on all endpoints
- [ ] Rate limiting active (verify 429 response after 60+ requests)
- [ ] User scoping verified: users cannot access others' data
- [ ] Conversation persistence: send messages, restart server, retrieve conversation
- [ ] Error handling: invalid messages return 400, AI errors return 503
- [ ] Performance: <3s response time for 95% of requests under load test
- [ ] API documentation updated with examples
- [ ] Frontend API client created (Spec-5 ready)

## Troubleshooting

### Issue: "OpenAI API key not set"
**Solution**: Verify `OPENAI_API_KEY` in `.env` and restart server.

### Issue: MCP tool execution fails
**Check**:
- Tool name matches function name
- Parameters passed in correct format
- User_id present in context
- Task service functions accessible

### Issue: Conversation messages not persisting
**Check**:
- Database transaction committed
- Foreign key constraints satisfied
- Alembic migration applied
- SQLModel relationships configured

### Issue: "User can access others' conversations"
**Immediate action**: Review all queries - ensure `WHERE user_id = ?` clause present
**Audit**: Check for missing ownership checks in services

### Issue: Rate limiting not working
**Check**:
- Middleware applied to chat endpoint
- `user_id` correctly extracted from JWT
- Rate limiter storage configured (in-memory or Redis)

## Performance Testing

Use `curl` or `postman` to verify:

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer <valid-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test performance"}'

# Test conversation list
curl http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer <valid-jwt-token>"
```

For load testing, use `locust` or `k6`:
```bash
# Example with k6
k6 run --vus 50 --duration 30s script.js
```

## Next Steps After Implementation

1. Update `tasks.md` with implementation tasks (if `/sp.tasks` not used)
2. Run full test suite and fix failures
3. Perform security audit (user scoping, JWT validation)
4. Load test to verify performance targets
5. Update wireframes/API documentation for frontend team
6. Create demo script for hackathon judges
7. Commit changes with proper conventional commit messages
8. Create PR and request review

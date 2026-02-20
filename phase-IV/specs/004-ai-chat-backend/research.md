# Research: AI Chat Backend & MCP Tools

**Feature**: 004-ai-chat-backend
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document consolidates research findings for implementing the AI chat backend with MCP tools integration.

## Research Areas

### 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK with function calling for tool orchestration

**Rationale**:
- Native integration with OpenAI models (GPT-4, GPT-3.5-turbo)
- Built-in support for function calling and tool execution
- Handles conversation context and message history
- Supports system prompts for agent behavior customization
- Well-documented Python SDK

**Alternatives Considered**:
- LangChain: More complex, requires additional abstraction layers
- Direct OpenAI API: More manual work for tool orchestration
- AutoGPT: Too heavy for task management use case

**Implementation Notes**:
- Agent initialized with system prompt defining task management behavior
- Tools registered as functions with JSON schemas
- Agent maintains conversation context internally but we persist externally
- Use GPT-4 for better instruction following and tool selection

### 2. MCP (Model Context Protocol) SDK

**Decision**: Use official MCP Python SDK for tool implementation

**Rationale**:
- Standardized protocol for AI tool integration
- Official support from Anthropic/MCP team
- Built-in validation and error handling
- Supports both synchronous and asynchronous operations
- Clear separation between tool interface and implementation

**Alternatives Considered**:
- Custom tool interface: Less standardized, harder to maintain
- LangChain tools: Vendor lock-in to LangChain ecosystem
- Direct function calls: No standardized interface

**Implementation Notes**:
- Create MCP server in `backend/src/mcp/server.py`
- Each task operation (add, list, complete, delete, update) as separate tool
- Tools accept structured input (JSON) and return structured output
- Tools interact with existing `task_service.py` for database operations
- User ID injected into tool context for data isolation

### 3. Conversation Context Management

**Decision**: Load last 20 messages from database on each request

**Rationale**:
- Stateless architecture requires reconstructing context per request
- 20 messages provides sufficient context while managing token limits
- Messages retrieved chronologically from database
- Efficient querying with indexed conversation_id and created_at
- OpenAI agent receives full context for coherent responses

**Alternatives Considered**:
- Summarization: Additional complexity, potential loss of important details
- Embedding-based retrieval: Overkill for task management conversations
- Fixed window (10 messages): May lose important context

**Implementation Notes**:
- Query: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 20`
- Reverse order before passing to agent (chronological)
- Include system message at start of conversation history
- Track token usage and warn if approaching model limits

### 4. Message Persistence Strategy

**Decision**: Immediate persistence for both user and AI messages

**Rationale**:
- Ensures no message loss
- Enables conversation retrieval after failures
- Supports conversation history browsing
- Simple implementation with no caching complexity
- Database transactions ensure consistency

**Alternatives Considered**:
- Batch persistence: Risk of data loss on failure
- Async persistence: Complex error handling
- In-memory buffer: Violates stateless principle

**Implementation Notes**:
- User message persisted before processing
- AI response persisted after generation
- Use database transactions for atomic operations
- Include timestamps for both sender types
- Store message metadata (token count, model version)

### 5. JWT Verification & User Scoping

**Decision**: Extract user ID from JWT, pass to all services and MCP tools

**Rationale**:
- Consistent with existing authentication pattern
- User ID available throughout request lifecycle
- No need for additional database lookups
- Security context propagated explicitly
- Easy to audit and debug

**Implementation Notes**:
- Use existing `verify_token()` from `auth/security.py`
- Extract `user_id` from JWT payload
- Pass `user_id` to chat_service, conversation_service, and MCP tools
- All database queries filter by `user_id`
- Rate limiting keyed by `user_id`

### 6. Rate Limiting Strategy

**Decision**: In-memory rate limiting with sliding window (60 req/min per user)

**Rationale**:
- Prevents abuse and manages OpenAI API costs
- Simple in-memory implementation sufficient for single server
- Sliding window provides smooth rate limiting
- Can upgrade to Redis for distributed deployment
- Per-user limits ensure fairness

**Alternatives Considered**:
- Token bucket: More complex, unnecessary for this use case
- Fixed window: Can allow burst at window boundaries
- No rate limiting: Risk of abuse and cost overruns

**Implementation Notes**:
- Use `slowapi` or custom middleware
- Store request timestamps per user
- Clean up old entries to prevent memory leaks
- Return 429 status code with retry-after header
- Log rate limit events for monitoring

### 7. Error Handling & Conversational Responses

**Decision**: Catch all exceptions, translate to natural language via agent

**Rationale**:
- Users should never see technical error messages
- Agent can provide helpful guidance in conversational tone
- Centralized error handling reduces code duplication
- Logging preserves technical details for debugging
- User-friendly responses maintain good UX

**Implementation Notes**:
- Wrap entire chat flow in try-except
- Log technical error details
- Pass error context to agent for user-friendly translation
- Specific handling for: database errors, OpenAI API errors, validation errors
- Always return valid JSON response structure

### 8. MCP Tool Input/Output Formats

**Decision**: Use JSON Schema for validation, structured dicts for I/O

**Rationale**:
- JSON Schema enables automatic validation
- Compatible with OpenAI function calling
- Clear contract for each tool
- Easy to test and debug
- Pydantic models provide runtime validation

**Tool Schemas**:

```python
# add_task
Input: {"title": str, "description": Optional[str]}
Output: {"success": bool, "task": Task, "message": str}

# list_tasks
Input: {}
Output: {"success": bool, "tasks": List[Task], "message": str}

# complete_task
Input: {"task_id": int}
Output: {"success": bool, "task": Task, "message": str}

# delete_task
Input: {"task_id": int}
Output: {"success": bool, "message": str}

# update_task
Input: {"task_id": int, "title": Optional[str], "description": Optional[str]}
Output: {"success": bool, "task": Task, "message": str}
```

### 9. API Contract Design

**Decision**: RESTful endpoints with JSON request/response

**Endpoints**:

```
POST /api/v1/chat/
  Request: {"message": str, "conversation_id": Optional[str]}
  Response: {
    "conversation_id": str,
    "message": {
      "content": str,
      "sender": "ai",
      "timestamp": str
    },
    "context": {
      "tasks_modified": List[int],
      "action_taken": str
    }
  }

GET /api/v1/conversations/
  Response: {
    "conversations": [
      {
        "id": str,
        "created_at": str,
        "message_count": int,
        "last_message": str
      }
    ]
  }

GET /api/v1/conversations/{conversation_id}
  Response: {
    "conversation": {
      "id": str,
      "created_at": str,
      "messages": [
        {
          "content": str,
          "sender": str,
          "timestamp": str
        }
      ]
    }
  }
```

**Rationale**:
- Consistent with existing API patterns
- Clear separation of concerns
- Easy for frontend to consume
- Supports pagination for conversation lists
- Includes metadata for rich UI rendering

### 10. Database Schema Extensions

**Decision**: Add `conversations` and `messages` tables with foreign key relationships

**Rationale**:
- Normalized schema prevents data duplication
- Foreign keys ensure referential integrity
- Indexed columns enable efficient querying
- Compatible with existing SQLModel patterns
- Easy to migrate with Alembic

**Schema**:

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sender VARCHAR NOT NULL,  -- 'user' or 'ai'
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB,  -- token count, model, etc.
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at)
);
```

## Dependencies & Risks

### Dependencies
- OpenAI API availability and response time
- Neon PostgreSQL performance for message queries
- Existing authentication system (Better Auth, JWT)
- Existing task models and services

### Risks & Mitigations
1. **OpenAI API Latency**: Implement timeout (5s), graceful degradation, retry logic
2. **Token Limit Exceeded**: Monitor usage, implement message summarization if needed
3. **Database Performance**: Index frequently queried columns, add caching if needed
4. **Cost Overruns**: Rate limiting, usage monitoring, budget alerts
5. **Context Loss**: Ensure all messages persisted, test conversation recovery

## Next Steps

Proceed to Phase 1 to design:
1. Data models (`data-model.md`)
2. API contracts (`contracts/chat-api.yaml`)
3. MCP tool documentation (`contracts/mcp-tools.md`)
4. Quickstart guide (`quickstart.md`)

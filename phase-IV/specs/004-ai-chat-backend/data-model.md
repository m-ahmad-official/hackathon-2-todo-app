# Data Model: AI Chat Backend & MCP Tools

**Feature**: 004-ai-chat-backend
**Date**: 2026-02-08
**Status**: Draft

## Overview

This document defines the data models for conversations and messages, extending the existing task management system to support AI-powered chat interactions.

## Entities

### Conversation

Represents a chat session between a user and the AI assistant.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier
- `user_id` (String, Required): Owner of the conversation (from JWT)
- `created_at` (DateTime, Auto): Conversation creation timestamp
- `updated_at` (DateTime, Auto): Last message timestamp
- `title` (String, Optional): Auto-generated or user-defined title

**Relationships**:
- One-to-Many with `Message` (a conversation has many messages)
- Many-to-One with `User` (many conversations belong to one user)

**Validation Rules**:
- `user_id` must match authenticated user from JWT
- `created_at` and `updated_at` are immutable after creation
- `title` limited to 200 characters if provided

**State Transitions**:
- New conversation: created when first message sent
- Active conversation: updated_at changes with new messages
- Archived conversation: no state change, only for retention policy

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    title: Optional[str] = Field(default=None, max_length=200)

    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message

Individual messages within a conversation.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier
- `conversation_id` (Integer, Foreign Key): Parent conversation
- `content` (Text, Required): Message text
- `sender` (Enum, Required): 'user' or 'ai'
- `created_at` (DateTime, Auto): Message timestamp
- `metadata` (JSON, Optional): Token count, model version, etc.

**Relationships**:
- Many-to-One with `Conversation` (many messages belong to one conversation)

**Validation Rules**:
- `content` must not be empty
- `content` limited to 10,000 characters
- `sender` must be 'user' or 'ai'
- `conversation_id` must reference existing conversation owned by user
- `created_at` is immutable after creation

**Metadata Structure**:

```json
{
  "token_count": 150,
  "model": "gpt-4",
  "finish_reason": "stop",
  "tools_called": ["add_task"]
}
```

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import json

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True, nullable=False)
    content: str = Field(max_length=10000, nullable=False)
    sender: str = Field(nullable=False)  # 'user' or 'ai'
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    conversation: Conversation = Relationship(back_populates="messages")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Task (Existing - Updated)

Existing task model extended with relationships to track which tasks were modified in conversations.

**New Fields** (optional tracking):
- No schema changes required
- Task modifications tracked in message metadata

**Relationships**:
- Tasks referenced in conversation context but not directly linked
- User isolation maintained through `user_id` filtering

## Database Schema

### PostgreSQL Tables

```sql
-- Conversations table
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    title VARCHAR(200)
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_created_at ON conversation(created_at);

-- Messages table
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'ai')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);
CREATE INDEX idx_message_conversation_created ON message(conversation_id, created_at DESC);

-- Trigger to update conversation.updated_at on new message
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON message
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

## Migration Strategy

### Alembic Migration

Create migration to add new tables:

```bash
alembic revision --autogenerate -m "Add conversations and messages tables"
alembic upgrade head
```

### Data Migration

- No data migration required (new tables)
- Existing tasks remain unchanged
- New conversations created as users start chatting

## Query Patterns

### Common Queries

1. **Get user's conversations**:
```sql
SELECT * FROM conversation
WHERE user_id = ?
ORDER BY updated_at DESC
LIMIT 20 OFFSET ?;
```

2. **Get conversation messages**:
```sql
SELECT * FROM message
WHERE conversation_id = ?
ORDER BY created_at ASC;
```

3. **Get recent messages for context**:
```sql
SELECT * FROM message
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 20;
```

4. **Count user's conversations**:
```sql
SELECT COUNT(*) FROM conversation WHERE user_id = ?;
```

5. **Get conversation metadata**:
```sql
SELECT
    c.*,
    COUNT(m.id) as message_count,
    (SELECT content FROM message WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message
FROM conversation c
LEFT JOIN message m ON c.id = m.conversation_id
WHERE c.user_id = ?
GROUP BY c.id
ORDER BY c.updated_at DESC;
```

## Performance Considerations

### Indexes
- `conversation.user_id`: Filter conversations by user
- `conversation.created_at`: Sort conversations chronologically
- `message.conversation_id`: Join with conversations
- `message.created_at`: Sort messages chronologically
- Composite index `(conversation_id, created_at DESC)`: Optimize recent message retrieval

### Query Optimization
- Use pagination for conversation lists (20 per page)
- Limit context retrieval to 20 most recent messages
- Use `SELECT` specific fields instead of `SELECT *` where appropriate
- Consider adding `EXPLAIN ANALYZE` to slow queries

### Storage Estimates
- Average message: 500 characters (~0.5 KB)
- Average conversation: 50 messages (~25 KB)
- 1000 users × 10 conversations × 25 KB = ~250 MB
- Metadata overhead: ~20% additional storage

## Validation & Constraints

### Application-Level Validation
- User can only access their own conversations
- Message content length validated before database insert
- Conversation ownership verified before message retrieval
- Sender type validated against enum values

### Database-Level Constraints
- Foreign key constraints ensure referential integrity
- `ON DELETE CASCADE` removes messages when conversation deleted
- `CHECK` constraint on sender field
- `NOT NULL` constraints on required fields

## Retention Policy

### Implementation
- Messages older than 90 days moved to archive table
- Archive queries slower but still accessible
- Cron job runs daily to move old messages
- Users can export conversations before archival

### Archive Schema
```sql
CREATE TABLE message_archive (LIKE message INCLUDING ALL);
CREATE TABLE conversation_archive (LIKE conversation INCLUDING ALL);
```

## Next Steps

1. Create Alembic migration for schema changes
2. Implement SQLModel classes in `models/conversation.py` and `models/message.py`
3. Create database service functions in `services/conversation_service.py`
4. Add tests for model validation and relationships

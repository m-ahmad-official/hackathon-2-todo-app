"""
Chat API documentation for the AI chat backend.

This module provides comprehensive OpenAPI documentation for all chat endpoints,
including request/response schemas, authentication requirements, error responses,
and detailed descriptions.
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from fastapi import Query, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field # Import BaseModel and Field from pydantic
from src.models.conversation import Conversation, ConversationResponse, ConversationCreate
from src.models.message import Message, MessageResponse
from src.core.database import get_session
from src.auth.deps import get_current_user_id
from src.services.conversation_service import ConversationService
from src.core.logging import log_operation


# Schemas for OpenAPI documentation
class ChatErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime
    path: str


class MessageCreate(BaseModel):
    """Schema for creating messages."""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content (max 10,000 characters)")
    sender: str = Field(..., description="Message sender ('user' or 'ai')")
    metadata: Optional[Dict] = Field(default=None, description="Optional message metadata")


class MessageListResponse(BaseModel):
    """Schema for message list responses."""
    messages: List[MessageResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class ConversationListResponse(BaseModel):
    """Schema for conversation list responses."""
    conversations: List[ConversationResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class ChatRequest(BaseModel):
    """Schema for chat requests."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message (1-10,000 characters)")
    conversation_id: Optional[int] = Field(default=None, description="Optional conversation ID to continue")


class ChatResponse(BaseModel):
    """Schema for chat responses."""
    conversation_id: int = Field(..., alias="conversationId", description="Conversation ID")
    message: str = Field(..., description="AI response message")
    context_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about actions taken (tasks modified, tools called, etc.)"
    )

    class Config:
        allow_population_by_field_name = True


# Documentation constants
ERROR_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ChatErrorResponse,
        "description": "Invalid request data"
    },
    status.HTTP_401_UNAUTHORIZED: {
        "model": ChatErrorResponse,
        "description": "Unauthorized - missing or invalid JWT token"
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ChatErrorResponse,
        "description": "Forbidden - access denied"
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ChatErrorResponse,
        "description": "Resource not found"
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": ChatErrorResponse,
        "description": "Internal server error"
    },
}


# Example requests and responses
EXAMPLE_CONVERSATION_CREATE_REQUEST = {
    "title": "My First Conversation"
}

EXAMPLE_CONVERSATION_CREATE_RESPONSE = {
    "id": 1,
    "user_id": "user-123",
    "title": "My First Conversation",
    "created_at": "2024-01-15T10:30:00.000000",
    "updated_at": "2024-01-15T10:30:00.000000",
    "message_count": 0,
    "last_message": None
}

EXAMPLE_MESSAGE_CREATE_REQUEST = {
    "content": "Hello! I need help with my project.",
    "sender": "user"
}

EXAMPLE_MESSAGE_CREATE_RESPONSE = {
    "id": 1,
    "conversation_id": 1,
    "content": "Hello! I need help with my project.",
    "sender": "user",
    "created_at": "2024-01-15T10:35:00.000000",
    "metadata": None
}

EXAMPLE_CONVERSATION_LIST_RESPONSE = {
    "conversations": [
        {
            "id": 1,
            "user_id": "user-123",
            "title": "My First Conversation",
            "created_at": "2024-01-15T10:30:00.000000",
            "updated_at": "2024-01-15T10:35:00.000000",
            "message_count": 1,
            "last_message": "Hello! I need help with my project."
        }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_more": False
}

EXAMPLE_MESSAGE_LIST_RESPONSE = {
    "messages": [
        {
            "id": 1,
            "conversation_id": 1,
            "content": "Hello! I need help with my project.",
            "sender": "user",
            "created_at": "2024-01-15T10:35:00.000000",
            "metadata": None
        }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_more": False
}


# Helper functions for documentation

def format_datetime(dt: datetime) -> str:
    """Format datetime for documentation examples."""
    return dt.isoformat(timespec="milliseconds")


def create_error_response(detail: str, error_code: str) -> ChatErrorResponse:
    """Create a standardized error response."""
    return ChatErrorResponse(
        detail=detail,
        error_code=error_code,
        timestamp=datetime.utcnow(),
        path=""  # Will be filled by FastAPI
    )


# Constants for authentication and security
AUTHENTICATION_REQUIRED = {
    "security": [{"bearerAuth": []}],
    "description": "JWT token required in Authorization header"
}

# CORS configuration for documentation
CORS_CONFIG = {
    "allow_origins": ["http://localhost:3000", "https://your-frontend-domain.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type", "Accept"]
}


# API version and documentation information
API_VERSION = "1.0.0"
API_DESCRIPTION = """
    AI Chat Backend API
    ===================

    This API provides endpoints for managing AI-powered chat conversations
    with user authentication and conversation management.

    Authentication:
    - All chat endpoints require JWT authentication
    - Use Bearer token in Authorization header
    - Tokens are obtained from the auth endpoints

    Data Models:
    - Conversations: Chat sessions with user-defined titles
    - Messages: Individual chat messages (user or AI)
    - Users: Authenticated users with unique IDs

    Error Handling:
    - Standard HTTP status codes
    - Detailed error responses with error codes
    - Logging for all operations
    """
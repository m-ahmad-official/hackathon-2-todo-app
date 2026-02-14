from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from src.services.conversation_service import ConversationService
from src.services.chat_service import ChatService
from src.models.conversation import Conversation, ConversationResponse, ConversationCreate
from src.models.message import Message, MessageResponse
from src.core.database import get_session
from src.core.logging import log_operation
from src.auth.deps import get_current_user_id
from src.auth.security import authorize_user_for_conversation
from src.api.v1.chat_docs import (
    ERROR_RESPONSES, MessageCreate, ChatErrorResponse,
    MessageListResponse, ConversationListResponse, ChatRequest, ChatResponse
)

router = APIRouter(
    tags=["chat"],
    responses=ERROR_RESPONSES
)

@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Create a new AI chat conversation for the authenticated user",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Conversation created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user-123",
                        "title": "My First Conversation",
                        "created_at": "2024-01-15T10:30:00.000000",
                        "updated_at": "2024-01-15T10:30:00.000000",
                        "message_count": 0,
                        "last_message": None
                    }
                }
            }
        }
    }
)

def create_conversation(
    conversation_create: ConversationCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ConversationResponse:
    """
    Create a new conversation for the authenticated user

    This endpoint creates a new AI chat conversation. The authenticated user
    is automatically assigned as the owner of the conversation.

    - **conversation_create**: Conversation creation data
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Security
    - Requires JWT authentication
    - User ID is automatically set to the authenticated user
    - Prevents user ID spoofing

    ## Response
    - Returns the created conversation with metadata
    - Includes message count and last message preview

    ## Error Responses
    - 400: Invalid request data
    - 401: Unauthorized (missing/invalid JWT token)
    - 500: Internal server error
    """
    try:
        # Override user_id with authenticated user's ID to ensure security
        conversation_create.user_id = current_user_id

        # Create the conversation
        db_conversation = ConversationService.create_conversation(session, current_user_id, conversation_create.title)

        log_operation("CONVERSATION_CREATED_SUCCESSFULLY", user_id=current_user_id, conversation_id=db_conversation.id)
        return ConversationResponse.model_validate(db_conversation)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("CREATE_CONVERSATION_ERROR", user_id=current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the conversation: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[ConversationResponse],
    summary="List user conversations",
    description="List all conversations for the authenticated user with pagination",
    responses={
        status.HTTP_200_OK: {
            "description": "Conversations retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
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
                }
            }
        }
    }
)

def list_conversations(
    limit: int = Query(default=20, ge=1, le=100, description="Number of conversations to return (1-100)"),
    offset: int = Query(default=0, ge=0, description="Number of conversations to skip"),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[ConversationResponse]:
    """
    List conversations for the authenticated user with pagination

    This endpoint returns a paginated list of conversations for the authenticated user.

    - **limit**: Number of conversations to return (1-100, default: 20)
    - **offset**: Number of conversations to skip (default: 0)
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Pagination
    - Use `limit` and `offset` parameters for pagination
    - Returns total count and has_more flag for client-side pagination

    ## Response
    - Returns list of conversation summaries
    - Each includes message count and last message preview

    ## Error Responses
    - 400: Invalid pagination parameters
    - 401: Unauthorized (missing/invalid JWT token)
    - 500: Internal server error
    """
    try:
        # Get conversations for the user
        conversations = ConversationService.list_conversations(session, current_user_id, limit, offset)

        log_operation(f"GET_CONVERSATIONS_SUCCESS ({len(conversations)} conversations)", user_id=current_user_id)

        # Return as response models using SQLModel's serialization
        return [ConversationResponse.model_validate(conversation, from_attributes=True) for conversation in conversations]
    except HTTPException:
        raise
    except Exception as e:
        log_operation("GET_CONVERSATIONS_ERROR", user_id=current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving conversations: {str(e)}"
        )

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation details",
    description="Get a specific conversation by ID with ownership verification",
    responses={
        status.HTTP_200_OK: {
            "description": "Conversation retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user-123",
                        "title": "My First Conversation",
                        "created_at": "2024-01-15T10:30:00.000000",
                        "updated_at": "2024-01-15T10:35:00.000000",
                        "message_count": 1,
                        "last_message": "Hello! I need help with my project."
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Conversation not found or access denied"
        }
    }
)

def get_conversation(
    conversation_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ConversationResponse:
    """
    Get a conversation by ID with ownership verification

    This endpoint retrieves a specific conversation. The user must own the
    conversation to access it (data isolation).

    - **conversation_id**: ID of the conversation to retrieve
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Security
    - Requires JWT authentication
    - Verifies user owns the conversation
    - Prevents unauthorized access to other users' conversations

    ## Response
    - Returns complete conversation details
    - Includes message count and last message preview

    ## Error Responses
    - 401: Unauthorized (missing/invalid JWT token)
    - 404: Conversation not found or access denied
    - 500: Internal server error
    """
    try:
        # Get the conversation from the database
        conversation = ConversationService.get_conversation(session, conversation_id, current_user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {conversation_id} not found or access denied"
            )

        log_operation("CONVERSATION_RETRIEVED_SUCCESSFULLY", user_id=current_user_id, conversation_id=conversation_id)
        return ConversationResponse.model_validate(conversation)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("GET_CONVERSATION_ERROR", user_id=current_user_id, conversation_id=conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the conversation: {str(e)}"
        )

@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Delete a conversation by ID (only if the conversation belongs to the authenticated user)",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Conversation deleted successfully"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Conversation not found or access denied"
        }
    }
)

def delete_conversation(
    conversation_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a conversation by ID (only if the conversation belongs to the authenticated user)

    This endpoint permanently deletes a conversation and all its messages.
    Only the conversation owner can delete their conversations.

    - **conversation_id**: ID of the conversation to delete
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Security
    - Requires JWT authentication
    - Verifies user owns the conversation
    - Permanently deletes conversation and messages

    ## Response
    - Returns 204 No Content on successful deletion
    - No response body

    ## Error Responses
    - 401: Unauthorized (missing/invalid JWT token)
    - 404: Conversation not found or access denied
    - 500: Internal server error
    """
    try:
        # Delete the conversation
        success = ConversationService.delete_conversation(session, conversation_id, current_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {conversation_id} not found or access denied"
            )

        log_operation("CONVERSATION_DELETED_SUCCESSFULLY", user_id=current_user_id, conversation_id=conversation_id)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("DELETE_CONVERSATION_ERROR", user_id=current_user_id, conversation_id=conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the conversation: {str(e)}"
        )

@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Get conversation messages",
    description="Get all messages in a conversation with ownership verification",
    responses={
        status.HTTP_200_OK: {
            "description": "Messages retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
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
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Conversation not found or access denied"
        }
    }
)

def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(default=20, ge=1, le=100, description="Number of messages to return (1-100)"),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[MessageResponse]:
    """
    Get all messages in a conversation with ownership verification

    This endpoint returns a paginated list of messages for a specific conversation.
    The user must own the conversation to access its messages.

    - **conversation_id**: ID of the conversation
    - **limit**: Number of messages to return (1-100, default: 20)
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Pagination
    - Use `limit` parameter for pagination
    - Returns messages in chronological order (oldest first)

    ## Message Types
    - `user`: Messages sent by the user
    - `ai`: Messages sent by the AI assistant

    ## Response
    - Returns list of message objects
    - Each includes sender, content, and timestamp

    ## Error Responses
    - 400: Invalid limit parameter
    - 401: Unauthorized (missing/invalid JWT token)
    - 404: Conversation not found or access denied
    - 500: Internal server error
    """
    try:
        # Verify that the user owns this conversation
        conversation = ConversationService.get_conversation(session, conversation_id, current_user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {conversation_id} not found or access denied"
            )

        # Get messages for the conversation
        messages = ConversationService.get_conversation_messages(session, conversation_id, limit)

        log_operation(f"GET_CONVERSATION_MESSAGES_SUCCESS ({len(messages)} messages)",
                    user_id=current_user_id, conversation_id=conversation_id)

        # Return as response models using SQLModel's serialization
        return [MessageResponse.model_validate(message, from_attributes=True) for message in messages]
    except HTTPException:
        raise
    except Exception as e:
        log_operation("GET_CONVERSATION_MESSAGES_ERROR", user_id=current_user_id, conversation_id=conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving conversation messages: {str(e)}"
        )

@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add message to conversation",
    description="Add a message to a conversation with ownership verification",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Message added successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "conversation_id": 1,
                        "content": "Hello! I need help with my project.",
                        "sender": "user",
                        "created_at": "2024-01-15T10:35:00.000000",
                        "metadata": None
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid message data (invalid sender or content)"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Conversation not found or access denied"
        }
    }
)

def add_message(
    conversation_id: int,
    content: str = Query(..., min_length=1, max_length=10000, description="Message content (1-10,000 characters)"),
    sender: str = Query(..., description="Message sender ('user' or 'ai')"),
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> MessageResponse:
    """
    Add a message to a conversation with ownership verification

    This endpoint adds a new message to a conversation. The user must own the
    conversation to add messages.

    - **conversation_id**: ID of the conversation
    - **content**: Message content (1-10,000 characters)
    - **sender**: Message sender ('user' or 'ai')
    - **metadata**: Optional message metadata
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Message Types
    - `user`: Messages sent by the user (human)
    - `ai`: Messages sent by the AI assistant

    ## Content Validation
    - Minimum 1 character, maximum 10,000 characters
    - Required field

    ## Metadata
    - Optional dictionary for additional message data
    - Can include timestamps, message IDs, or other custom data

    ## Response
    - Returns the created message with ID and timestamp
    - Includes conversation ID for reference

    ## Error Responses
    - 400: Invalid sender value or content length
    - 401: Unauthorized (missing/invalid JWT token)
    - 404: Conversation not found or access denied
    - 500: Internal server error
    """
    try:
        # Verify that the user owns this conversation
        conversation = ConversationService.get_conversation(session, conversation_id, current_user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with id {conversation_id} not found or access denied"
            )

        # Validate sender
        if sender not in ['user', 'ai']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sender must be 'user' or 'ai'"
            )

        # Add the message
        message = ConversationService.add_message(session, conversation_id, content, sender)

        log_operation("MESSAGE_ADDED_SUCCESSFULLY", user_id=current_user_id, conversation_id=conversation_id, message_id=message.id)
        return MessageResponse.model_validate(message)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("ADD_MESSAGE_ERROR", user_id=current_user_id, conversation_id=conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding the message: {str(e)}"
        )


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to AI agent",
    description="Send a natural language message to the AI agent for task management",
    responses={
        status.HTTP_200_OK: {
            "description": "Chat message processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "conversation_id": 1,
                        "message": "I've created a task 'Buy groceries' for you.",
                        "context_metadata": {
                            "tasks_modified": 1,
                            "action_taken": True,
                            "tool_calls": [{"tool": "add_task", "success": True}]
                        }
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized - missing or invalid JWT token"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Conversation not found (if conversation_id provided)"
        }
    }
)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Send a chat message to the AI agent

    This endpoint processes a natural language message through the AI agent,
    which can create, list, complete, update, or delete tasks based on
    the user's request.

    - **chat_request**: Chat request with message and optional conversation_id
    - **current_user_id**: Authenticated user ID (from JWT token)
    - **session**: Database session

    ## Conversation Handling
    - If conversation_id is provided: continues existing conversation
    - If conversation_id is not provided: creates new conversation

    ## AI Agent Capabilities
    - Create new tasks
    - List existing tasks
    - Mark tasks as complete
    - Update task properties
    - Delete tasks
    - Maintain conversation context

    ## Response
    - Returns AI response message
    - Includes conversation_id for future messages
    - Includes metadata about actions taken

    ## Error Responses
    - 401: Unauthorized (missing/invalid JWT token)
    - 404: Conversation not found (if conversation_id provided but invalid)
    - 500: Internal server error
    """
    try:
        # Initialize chat service
        chat_service = ChatService()

        # Process the chat message
        result = await chat_service.process_chat_message(
            session=session,
            user_id=current_user_id,
            message=chat_request.message,
            conversation_id=chat_request.conversation_id
        )

        log_operation("CHAT_MESSAGE_PROCESSED", user_id=current_user_id, conversation_id=result["conversation_id"])
        return ChatResponse(**result)

    except ValueError as e:
        log_operation("CHAT_MESSAGE_ERROR", user_id=current_user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        log_operation("CHAT_MESSAGE_ERROR", user_id=current_user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your message: {str(e)}"
        )
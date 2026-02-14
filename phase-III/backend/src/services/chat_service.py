"""
Chat Service - Orchestrates chat message processing with AI agent
"""

from typing import Optional, Dict, Any, List
from sqlmodel import Session
from src.services.conversation_service import ConversationService
from src.agent.chat_agent import ChatAgent
from src.agent.context_builder import ContextBuilder
from src.core.logging import log_operation


class ChatService:
    def __init__(self):
        """Initialize chat service with agent and context builder"""
        self.agent = ChatAgent()
        self.context_builder = ContextBuilder(max_messages=20, max_tokens=8000)

    async def process_chat_message(
        self,
        session: Session,
        user_id: str,
        message: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message through the AI agent

        Args:
            session: Database session
            user_id: ID of the authenticated user
            message: User's message text
            conversation_id: Optional existing conversation ID

        Returns:
            Dictionary with conversation_id, ai_response, and metadata
        """
        try:
            # Get or create conversation
            if conversation_id:
                conversation = ConversationService.get_conversation(
                    session, conversation_id, user_id
                )
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found or access denied")
            else:
                conversation = ConversationService.create_conversation(
                    session, user_id, title=None
                )
                conversation_id = conversation.id

            # Save user message
            ConversationService.add_message(
                session, conversation_id, message, "user"
            )
            log_operation("USER_MESSAGE_SAVED", user_id=user_id, conversation_id=conversation_id)

            # Load conversation context
            db_messages = ConversationService.get_recent_messages(
                session, conversation_id, limit=20
            )

            # Format messages for context
            context_messages = []
            for msg in db_messages:
                context_messages.append({
                    "sender": msg.sender,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                })

            # Reverse to chronological order for context builder
            context_messages.reverse()

            # Build context using context builder
            context = self.context_builder.build_context(context_messages)

            # Process through AI agent
            agent_result = await self.agent.process_message(
                message=message,
                context=context,
                user_id=user_id
            )

            ai_response = agent_result.get("ai_response", "I apologize, but I couldn't process your request.")
            tool_calls = agent_result.get("tool_calls", [])

            # Execute tool calls if any
            tool_results = []
            if tool_calls:
                tool_results = await self.agent.execute_tool_calls(
                    tool_calls=tool_calls,
                    user_id=user_id,
                    session=session
                )
                log_operation("TOOL_CALLS_EXECUTED", user_id=user_id, conversation_id=conversation_id, count=len(tool_results))

            # Save AI response
            ConversationService.add_message(
                session, conversation_id, ai_response, "ai"
            )
            log_operation("AI_RESPONSE_SAVED", user_id=user_id, conversation_id=conversation_id)

            # Build response
            response = {
                "conversation_id": conversation_id,
                "message": ai_response,
                "context_metadata": {
                    "tasks_modified": len([r for r in tool_results if r.get("success")]),
                    "action_taken": len(tool_calls) > 0,
                    "tool_calls": [
                        {"tool": tc.get("name"), "success": any(r.get("tool") == tc.get("name") and r.get("success") for r in tool_results)}
                        for tc in tool_calls
                    ] if tool_calls else []
                }
            }

            return response

        except Exception as e:
            log_operation("CHAT_SERVICE_ERROR", user_id=user_id, conversation_id=conversation_id, error=str(e))
            raise

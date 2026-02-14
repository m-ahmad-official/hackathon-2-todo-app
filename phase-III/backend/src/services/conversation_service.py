from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import Session
from sqlmodel import select
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task import Task

class ConversationService:
    @staticmethod
    def create_conversation(session: Session, user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for a user
        """
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(session: Session, conversation_id: int, user_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID with ownership verification
        """
        return session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

    @staticmethod
    def list_conversations(session: Session, user_id: str, limit: int = 20, offset: int = 0) -> List[Conversation]:
        """
        List conversations for a user with pagination
        """
        return session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()

    @staticmethod
    def delete_conversation(session: Session, conversation_id: int, user_id: str) -> bool:
        """
        Delete a conversation with ownership verification
        """
        conversation = ConversationService.get_conversation(session, conversation_id, user_id)
        if conversation:
            session.delete(conversation)
            session.commit()
            return True
        return False

    @staticmethod
    def add_message(session: Session, conversation_id: int, content: str, sender: str) -> Message:
        """
        Add a message to a conversation
        """
        message = Message(
            conversation_id=conversation_id,
            content=content,
            sender=sender
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        # Update conversation timestamp
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.commit()

        return message

    @staticmethod
    def get_conversation_messages(session: Session, conversation_id: int, limit: int = 20) -> List[Message]:
        """
        Get all messages in a conversation in chronological order
        """
        return session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        ).all()

    @staticmethod
    def get_recent_messages(session: Session, conversation_id: int, limit: int = 20) -> List[Message]:
        """
        Get recent messages for context (newest first)
        """
        return session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        ).all()

    @staticmethod
    def get_conversation_metadata(session: Session, conversation_id: int, user_id: str):
        """
        Get conversation metadata including message count and last message
        """
        conversation = ConversationService.get_conversation(session, conversation_id, user_id)
        if not conversation:
            return None

        message_count = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
        ).count()

        last_message = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        ).first()

        return {
            "conversation": conversation,
            "message_count": message_count,
            "last_message": last_message
        }
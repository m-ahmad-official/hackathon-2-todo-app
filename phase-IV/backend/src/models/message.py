from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True, nullable=False)
    content: str = Field(max_length=10000, nullable=False)
    sender: str = Field(nullable=False)  # 'user' or 'ai'
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Pydantic model for API responses
class MessageResponse(SQLModel):
    id: int
    conversation_id: int
    content: str
    sender: str
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def model_validate(cls, obj, from_attributes: bool = False):
        if from_attributes:
            return cls(
                id=obj.id,
                conversation_id=obj.conversation_id,
                content=obj.content,
                sender=obj.sender,
                created_at=obj.created_at
            )
        return super().model_validate(obj)
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    title: Optional[str] = Field(default=None, max_length=200)

    messages: List["Message"] = Relationship(back_populates="conversation")

# Pydantic models for API responses
class ConversationCreate(SQLModel):
    title: Optional[str] = None

class ConversationResponse(SQLModel):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    title: Optional[str] = None
    message_count: Optional[int] = None
    last_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def model_validate(cls, obj, from_attributes: bool = False):
        if from_attributes:
            return cls(
                id=obj.id,
                user_id=obj.user_id,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                title=obj.title
            )
        return super().model_validate(obj)
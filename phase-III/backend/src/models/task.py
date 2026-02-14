from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import select
from sqlmodel import Session
from pydantic import ConfigDict


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: str = Field(max_length=255)


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def get_by_user_id(cls, session: Session, user_id: str):
        """
        Class method to get all tasks for a specific user
        """
        statement = select(cls).where(cls.user_id == user_id)
        result = session.exec(statement)
        tasks = result.all()
        return tasks

    @classmethod
    def get_by_id_and_user_id(cls, session: Session, task_id: int, user_id: str):
        """
        Class method to get a specific task for a specific user (for data isolation)
        """
        statement = select(cls).where(cls.id == task_id, cls.user_id == user_id)
        return session.exec(statement).first()


class TaskCreate(TaskBase):
    user_id: Optional[str] = Field(default=None, max_length=255)  # Override to make optional for creation


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None


from pydantic import ConfigDict

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import Column, String


class UserBase(SQLModel):
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    name: Optional[str] = Field(default=None)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    class Config:
        from_attributes = True

    __table_args__ = {"extend_existing": True}


class UserCreate(UserBase):
    email: str
    password: str
    name: str


class UserPublic(UserBase):
    id: int
    email: str
    name: Optional[str] = None


class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None

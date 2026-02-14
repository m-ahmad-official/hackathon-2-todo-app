from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from src.api.v1 import tasks, chat
from src.api.v1.auth import router as auth_router
# from src.auth.middleware import JWTMiddleware  # Temporarily disabled
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import create_db_and_tables
from typing import Dict, List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, Field as PydanticField


class MessageResponse(BaseModel):
    """Pydantic model for message responses."""
    id: int
    conversation_id: int
    content: str
    sender: str
    created_at: datetime
    metadata: Optional[Dict] = None


class ConversationResponse(BaseModel):
    """Pydantic model for conversation responses."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    title: Optional[str] = None
    message_count: Optional[int] = None
    last_message: Optional[str] = None


class ConversationCreate(BaseModel):
    """Pydantic model for creating conversations."""
    title: Optional[str] = None


app = FastAPI(
    title="AI Chat Backend API",
    version="1.0.0",
    description="A RESTful API for AI-powered chat conversations with user authentication and conversation management.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()



# Include API routes
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

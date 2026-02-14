"""
MCP Tool: Create a new task
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.src.models.task import Task

class AddTaskInput(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None

class AddTaskOutput(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error: Optional[str] = None

async def add_task(input: AddTaskInput, context: Dict[str, Any]) -> AddTaskOutput:
    """
    MCP Tool: Create a new task

    Args:
        input: AddTaskInput with task details
        context: MCP context containing user_id and other metadata

    Returns:
        AddTaskOutput with success status and task ID or error
    """
    try:
        user_id = context.get("user_id")
        if not user_id:
            return AddTaskOutput(success=False, error="User ID not found in context")

        # Create task using existing task service
        from backend.src.services.task_service import TaskService
        from backend.src.core.database import get_session

        async with get_session() as session:
            task = TaskService.create_task(
                session,
                title=input.title,
                description=input.description,
                user_id=user_id
            )
            return AddTaskOutput(success=True, task_id=task.id)

    except Exception as e:
        return AddTaskOutput(success=False, error=str(e))
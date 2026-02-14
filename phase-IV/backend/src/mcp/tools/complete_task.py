"""
MCP Tool: Mark a task as complete
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class CompleteTaskInput(BaseModel):
    task_id: int

class CompleteTaskOutput(BaseModel):
    success: bool
    task_completed: Optional[bool] = None
    error: Optional[str] = None

async def complete_task(input: CompleteTaskInput, context: Dict[str, Any]) -> CompleteTaskOutput:
    """
    MCP Tool: Mark a task as complete

    Args:
        input: CompleteTaskInput with task_id
        context: MCP context containing user_id

    Returns:
        CompleteTaskOutput with success status
    """
    try:
        user_id = context.get("user_id")
        if not user_id:
            return CompleteTaskOutput(success=False, error="User ID not found in context")

        from backend.src.services.task_service import TaskService
        from backend.src.core.database import get_session

        async with get_session() as session:
            success = TaskService.update_task(
                session,
                task_id=input.task_id,
                user_id=user_id,
                completed=True
            )
            return CompleteTaskOutput(success=success, task_completed=True)

    except Exception as e:
        return CompleteTaskOutput(success=False, error=str(e))
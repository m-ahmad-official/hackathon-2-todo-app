"""
MCP Tool: Update task fields
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class UpdateTaskInput(BaseModel):
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class UpdateTaskOutput(BaseModel):
    success: bool
    task: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

async def update_task(input: UpdateTaskInput, context: Dict[str, Any]) -> UpdateTaskOutput:
    """
    MCP Tool: Update task fields

    Args:
        input: UpdateTaskInput with fields to update
        context: MCP context containing user_id

    Returns:
        UpdateTaskOutput with updated task
    """
    try:
        user_id = context.get("user_id")
        if not user_id:
            return UpdateTaskOutput(success=False, error="User ID not found in context")

        from backend.src.services.task_service import TaskService
        from backend.src.core.database import get_session

        async with get_session() as session:
            update_data = {}
            if input.title:
                update_data["title"] = input.title
            if input.description:
                update_data["description"] = input.description
            if input.completed is not None:
                update_data["completed"] = input.completed

            task = TaskService.update_task(
                session,
                task_id=input.task_id,
                user_id=user_id,
                **update_data
            )

            if task:
                return UpdateTaskOutput(success=True, task=task.model_dump())
            else:
                return UpdateTaskOutput(success=False, error="Task not found or unauthorized")

    except Exception as e:
        return UpdateTaskOutput(success=False, error=str(e))
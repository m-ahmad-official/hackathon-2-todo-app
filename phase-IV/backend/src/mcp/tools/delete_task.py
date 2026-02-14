"""
MCP Tool: Delete a task
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class DeleteTaskInput(BaseModel):
    task_id: int

class DeleteTaskOutput(BaseModel):
    success: bool
    task_deleted: Optional[bool] = None
    error: Optional[str] = None

async def delete_task(input: DeleteTaskInput, context: Dict[str, Any]) -> DeleteTaskOutput:
    """
    MCP Tool: Delete a task

    Args:
        input: DeleteTaskInput with task_id
        context: MCP context containing user_id

    Returns:
        DeleteTaskOutput with success status
    """
    try:
        user_id = context.get("user_id")
        if not user_id:
            return DeleteTaskOutput(success=False, error="User ID not found in context")

        from backend.src.services.task_service import TaskService
        from backend.src.core.database import get_session

        async with get_session() as session:
            success = TaskService.delete_task(
                session,
                task_id=input.task_id,
                user_id=user_id
            )
            return DeleteTaskOutput(success=success, task_deleted=True)

    except Exception as e:
        return DeleteTaskOutput(success=False, error=str(e))
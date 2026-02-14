"""
MCP Tool: List tasks with optional filters
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from backend.src.models.task import Task

class ListTasksInput(BaseModel):
    completed: Optional[bool] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class ListTasksOutput(BaseModel):
    success: bool
    tasks: List = []
    total: int = 0
    error: Optional[str] = None

async def list_tasks(input: ListTasksInput, context: Dict[str, Any]) -> ListTasksOutput:
    """
    MCP Tool: List tasks with optional filters

    Args:
        input: ListTasksInput with filter options
        context: MCP context containing user_id

    Returns:
        ListTasksOutput with task list and total count
    """
    try:
        user_id = context.get("user_id")
        if not user_id:
            return ListTasksOutput(success=False, error="User ID not found in context")

        from backend.src.services.task_service import TaskService
        from backend.src.core.database import get_session

        async with get_session() as session:
            tasks = TaskService.list_tasks(
                session,
                user_id=user_id,
                completed=input.completed,
                limit=input.limit,
                offset=input.offset
            )
            total = TaskService.count_tasks(session, user_id=user_id)

            return ListTasksOutput(
                success=True,
                tasks=[task.model_dump() for task in tasks],
                total=total
            )

    except Exception as e:
        return ListTasksOutput(success=False, error=str(e))
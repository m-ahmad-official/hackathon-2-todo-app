from typing import Optional
from src.models.task import TaskCreate, TaskUpdate
from fastapi import HTTPException, status


def validate_task_create(task_create: TaskCreate) -> None:
    """
    Validate task creation data
    """
    if not task_create.title or len(task_create.title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required"
        )

    if len(task_create.title) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title must be 255 characters or less"
        )

    if task_create.description and len(task_create.description) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task description must be 1000 characters or less"
        )

    # Skip user_id validation here since it will be set from JWT token
    # The user_id will be validated after it's set from the JWT
    # This validation should happen after the user_id is set in the endpoint


def validate_task_update(task_update: TaskUpdate) -> None:
    """
    Validate task update data
    """
    if task_update.title is not None:
        if len(task_update.title) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty"
            )
        if len(task_update.title) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title must be 255 characters or less"
            )

    if task_update.description is not None and len(task_update.description) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task description must be 1000 characters or less"
        )


def validate_user_access(task_user_id: str, requesting_user_id: Optional[str]) -> bool:
    """
    Validate that the requesting user has access to the task
    """
    if not requesting_user_id:
        return False
    return task_user_id == requesting_user_id
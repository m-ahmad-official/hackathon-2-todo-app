from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.services.task_service import TaskService
from src.models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from src.core.database import get_session
from src.core.logging import log_operation
from src.auth.deps import get_current_user_id
from src.auth.security import authorize_user_for_task

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_create: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user
    """
    try:
        from src.utils.validators import validate_task_create

        # Override user_id with authenticated user's ID to ensure security
        task_create.user_id = current_user_id

        # Now validate the task with the proper user_id
        validate_task_create(task_create)

        # Create the task
        db_task = TaskService.create_task(session, task_create)

        log_operation("TASK_CREATED_SUCCESSFULLY", user_id=current_user_id, task_id=db_task.id)
        return TaskResponse.model_validate(db_task)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("CREATE_TASK_ERROR", user_id=current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the task: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[TaskResponse])
def get_tasks_for_user(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[TaskResponse]:
    """
    Get all tasks for the authenticated user
    """
    try:
        # Verify that the requested user_id matches the authenticated user's ID
        if user_id != current_user_id:
            log_operation(f"UNAUTHORIZED_ACCESS_ATTEMPT_tasks_for_user_{user_id}", user_id=current_user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own tasks"
            )

        # Validate that user_id is provided
        if not user_id or len(user_id.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )

        # Get tasks for the user
        tasks = TaskService.get_tasks_by_user_id(session, user_id)

        log_operation(f"GET_TASKS_SUCCESS ({len(tasks)} tasks)", user_id=user_id)

        # Return as response models using SQLModel's serialization
        return [TaskResponse.model_validate(task, from_attributes=True) for task in tasks]
    except HTTPException:
        raise
    except Exception as e:
        log_operation("GET_TASKS_ERROR", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving tasks: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update a task by ID (only if the task belongs to the authenticated user)
    """
    try:
        from src.utils.validators import validate_task_update
        validate_task_update(task_update)

        # Get the task from the database
        existing_task = TaskService.get_task_by_id(session, task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        # Verify that the authenticated user owns this task
        if existing_task.user_id != current_user_id:
            log_operation("UNAUTHORIZED_ACCESS_ATTEMPT", user_id=current_user_id, task_id=task_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own tasks"
            )

        # Update the task
        updated_task = TaskService.update_task(session, task_id, task_update)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        log_operation("TASK_UPDATED_SUCCESSFULLY", user_id=current_user_id, task_id=task_id)
        return TaskResponse.model_validate(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("UPDATE_TASK_ERROR", user_id=current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the task: {str(e)}"
        )


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task_completion(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Toggle the completion status of a task (only if the task belongs to the authenticated user)
    """
    try:
        # Get the task from the database
        existing_task = TaskService.get_task_by_id(session, task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        # Verify that the authenticated user owns this task
        if existing_task.user_id != current_user_id:
            log_operation("UNAUTHORIZED_ACCESS_ATTEMPT", user_id=current_user_id, task_id=task_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only toggle completion status of your own tasks"
            )

        # Toggle the task completion status
        toggled_task = TaskService.toggle_task_completion(session, task_id)
        if not toggled_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        log_operation("TASK_COMPLETION_TOGGLED_SUCCESSFULLY", user_id=current_user_id, task_id=task_id)
        return TaskResponse.model_validate(toggled_task)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("TOGGLE_TASK_ERROR", user_id=current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while toggling the task: {str(e)}"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a task by ID (only if the task belongs to the authenticated user)
    """
    try:
        # Get the task from the database
        existing_task = TaskService.get_task_by_id(session, task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        # Verify that the authenticated user owns this task
        if existing_task.user_id != current_user_id:
            log_operation("UNAUTHORIZED_ACCESS_ATTEMPT", user_id=current_user_id, task_id=task_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own tasks"
            )

        # Delete the task
        success = TaskService.delete_task(session, task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )

        log_operation("TASK_DELETED_SUCCESSFULLY", user_id=current_user_id, task_id=task_id)
    except HTTPException:
        raise
    except Exception as e:
        log_operation("DELETE_TASK_ERROR", user_id=current_user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the task: {str(e)}"
        )
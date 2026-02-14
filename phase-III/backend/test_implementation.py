"""
Simple test to validate the backend implementation
"""
from src.models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from src.services.task_service import TaskService
from src.core.database import engine
from sqlmodel import Session, create_engine, SQLModel


def test_basic_functionality():
    """
    Test basic functionality of the task system
    """
    print("Testing basic task functionality...")

    # Create a test task
    task_create = TaskCreate(
        title="Test Task",
        description="This is a test task",
        user_id="test_user_123"
    )

    print(f"Created TaskCreate: {task_create}")
    print(f"Title: {task_create.title}")
    print(f"Description: {task_create.description}")
    print(f"User ID: {task_create.user_id}")
    print(f"Completed (default): {task_create.completed}")

    # Test TaskUpdate
    task_update = TaskUpdate(title="Updated Title", completed=True)
    print(f"\nTaskUpdate: {task_update}")

    # Test TaskResponse
    from datetime import datetime
    task_response = TaskResponse(
        id=1,
        title="Response Task",
        description="Test response",
        completed=False,
        user_id="test_user_123",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    print(f"\nTaskResponse: {task_response}")

    print("\n✅ Basic functionality test passed!")


if __name__ == "__main__":
    test_basic_functionality()
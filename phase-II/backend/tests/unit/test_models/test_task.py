import pytest
from datetime import datetime
from src.models.task import Task, TaskCreate, TaskUpdate, TaskResponse


def test_task_creation():
    """Test creating a basic task"""
    task_create = TaskCreate(
        title="Test Task",
        description="Test Description",
        user_id="user123"
    )

    assert task_create.title == "Test Task"
    assert task_create.description == "Test Description"
    assert task_create.user_id == "user123"
    assert task_create.completed is False  # Default value


def test_task_with_completed_true():
    """Test creating a task with completed=True"""
    task_create = TaskCreate(
        title="Completed Task",
        description="A completed task",
        completed=True,
        user_id="user123"
    )

    assert task_create.completed is True


def test_task_minimal_fields():
    """Test creating a task with minimal required fields"""
    task_create = TaskCreate(
        title="Minimal Task",
        user_id="user123"
    )

    assert task_create.title == "Minimal Task"
    assert task_create.user_id == "user123"
    assert task_create.description is None
    assert task_create.completed is False


def test_task_response_model():
    """Test the TaskResponse model"""
    task_response = TaskResponse(
        id=1,
        title="Response Task",
        description="A task response",
        completed=False,
        user_id="user123",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    assert task_response.id == 1
    assert task_response.title == "Response Task"
    assert task_response.description == "A task response"
    assert task_response.completed is False
    assert task_response.user_id == "user123"


def test_task_update_model():
    """Test the TaskUpdate model"""
    task_update = TaskUpdate(
        title="Updated Title",
        description="Updated Description",
        completed=True
    )

    assert task_update.title == "Updated Title"
    assert task_update.description == "Updated Description"
    assert task_update.completed is True


def test_task_update_partial():
    """Test partial updates in TaskUpdate model"""
    task_update = TaskUpdate(title="Only Title Updated")

    assert task_update.title == "Only Title Updated"
    # Other fields should be None since they're optional
    assert task_update.description is None
    assert task_update.completed is None
import pytest
from src.todo_service import TodoService

def test_add_task():
    service = TodoService()
    task = service.add_task("Buy groceries")
    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.is_completed is False
    assert len(service.get_all_tasks()) == 1

def test_add_empty_task_raises_error():
    service = TodoService()
    with pytest.raises(ValueError, match="Task title cannot be empty."):
        service.add_task("   ")

def test_get_all_tasks():
    service = TodoService()
    service.add_task("Task 1")
    service.add_task("Task 2")
    tasks = service.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"

def test_toggle_completion():
    service = TodoService()
    task = service.add_task("Verify toggle")
    service.toggle_completion(task.id)
    assert task.is_completed is True
    service.toggle_completion(task.id)
    assert task.is_completed is False

def test_update_task():
    service = TodoService()
    task = service.add_task("Old Title")
    service.update_task(task.id, "New Title")
    assert task.title == "New Title"

def test_delete_task():
    service = TodoService()
    task = service.add_task("To be deleted")
    assert len(service.get_all_tasks()) == 1
    service.delete_task(task.id)
    assert len(service.get_all_tasks()) == 0

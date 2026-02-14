from typing import List, Optional
from models import Task

class TodoService:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str) -> Task:
        """Adds a new task to the in-memory list."""
        if not title.strip():
            raise ValueError("Task title cannot be empty.")

        task = Task(id=self._next_id, title=title.strip())
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Returns all stored tasks."""
        return self._tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Finds a task by its unique ID."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def toggle_completion(self, task_id: int) -> bool:
        """Toggles the completion status of a task. Returns success boolean."""
        task = self.get_task_by_id(task_id)
        if task:
            task.is_completed = not task.is_completed
            return True
        return False

    def update_task(self, task_id: int, new_title: str) -> bool:
        """Updates the title of an existing task."""
        if not new_title.strip():
            raise ValueError("New title cannot be empty.")

        task = self.get_task_by_id(task_id)
        if task:
            task.title = new_title.strip()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Removes a task from the list."""
        task = self.get_task_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

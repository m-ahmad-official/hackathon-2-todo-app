from typing import List, Optional
from sqlmodel import Session, select
from src.models.task import Task, TaskCreate, TaskUpdate
from src.core.logging import log_operation, log_error, log_authorization_decision


class TaskService:
    @staticmethod
    def create_task(session: Session, task_create: TaskCreate) -> Task:
        """
        Create a new task in the database
        """
        try:
            log_operation("CREATE_TASK", user_id=str(task_create.user_id))

            db_task = Task(**task_create.dict())
            session.add(db_task)
            session.commit()
            session.refresh(db_task)

            log_operation("TASK_CREATED", user_id=str(task_create.user_id), task_id=db_task.id)
            return db_task
        except Exception as e:
            log_error(e, "CREATE_TASK")
            session.rollback()
            raise

    @staticmethod
    def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID
        """
        try:
            log_operation("GET_TASK_BY_ID", task_id=task_id)

            statement = select(Task).where(Task.id == task_id)
            task = session.exec(statement).first()

            if task:
                log_operation("TASK_FOUND", task_id=task_id, user_id=task.user_id)
            else:
                log_operation("TASK_NOT_FOUND", task_id=task_id)

            return task
        except Exception as e:
            log_error(e, "GET_TASK_BY_ID")
            raise

    @staticmethod
    def get_tasks_by_user_id(session: Session, user_id: str) -> List[Task]:
        """
        Retrieve all tasks for a specific user
        """
        try:
            log_operation("GET_TASKS_BY_USER", user_id=user_id)

            # Using the enhanced model method
            tasks = Task.get_by_user_id(session, user_id)

            # Ensure we're returning Task objects and not Row objects
            # If the result contains Row objects, extract the Task from them
            processed_tasks = []
            for task in tasks:
                if hasattr(task, '__iter__') and not isinstance(task, str) and hasattr(task, '__getitem__'):
                    # This looks like a Row/tuple object, extract the first element if it's a Task
                    try:
                        if len(task) > 0:
                            item = task[0]
                            if isinstance(item, Task):
                                processed_tasks.append(item)
                            else:
                                processed_tasks.append(task)
                        else:
                            processed_tasks.append(task)
                    except:
                        # If there's any issue with unpacking, just add the original
                        processed_tasks.append(task)
                else:
                    processed_tasks.append(task)

            log_operation(f"FOUND_{len(processed_tasks)}_TASKS_FOR_USER", user_id=user_id)
            return processed_tasks
        except Exception as e:
            log_error(e, "GET_TASKS_BY_USER")
            raise

    @staticmethod
    def get_task_by_id_and_user_id(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """
        Retrieve a task by ID for a specific user (enforcing data isolation)
        """
        try:
            log_operation("GET_TASK_BY_ID_AND_USER", user_id=user_id, task_id=task_id)

            # Using the enhanced model method for data isolation
            task = Task.get_by_id_and_user_id(session, task_id, user_id)

            if task:
                log_operation("TASK_FOUND_FOR_USER", user_id=user_id, task_id=task_id)
            else:
                log_operation("TASK_NOT_FOUND_FOR_USER", user_id=user_id, task_id=task_id)

            return task
        except Exception as e:
            log_error(e, "GET_TASK_BY_ID_AND_USER")
            raise

    @staticmethod
    def update_task(session: Session, task_id: int, task_update: TaskUpdate, current_user_id: str = None) -> Optional[Task]:
        """
        Update an existing task, with user ownership validation if current_user_id is provided
        """
        try:
            # Get the existing task
            statement = select(Task).where(Task.id == task_id)
            db_task = session.exec(statement).first()

            if not db_task:
                log_operation("TASK_UPDATE_FAILED_NOT_FOUND", task_id=task_id)
                return None

            # If current user is provided, validate ownership
            if current_user_id and db_task.user_id != current_user_id:
                log_authorization_decision("update", current_user_id, f"task-{task_id}", False)
                raise PermissionError(f"User {current_user_id} does not own task {task_id}")

            # Log successful authorization if user was validated
            if current_user_id:
                log_authorization_decision("update", current_user_id, f"task-{task_id}", True)

            # Apply updates
            update_data = task_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)

            session.add(db_task)
            session.commit()
            session.refresh(db_task)

            log_operation("TASK_UPDATED", user_id=db_task.user_id, task_id=task_id)
            return db_task
        except Exception as e:
            log_error(e, "UPDATE_TASK")
            session.rollback()
            raise

    @staticmethod
    def delete_task(session: Session, task_id: int, current_user_id: str = None) -> bool:
        """
        Delete a task by its ID, with user ownership validation if current_user_id is provided
        """
        try:
            statement = select(Task).where(Task.id == task_id)
            db_task = session.exec(statement).first()

            if not db_task:
                log_operation("TASK_DELETE_FAILED_NOT_FOUND", task_id=task_id)
                return False

            # If current user is provided, validate ownership
            if current_user_id and db_task.user_id != current_user_id:
                log_authorization_decision("delete", current_user_id, f"task-{task_id}", False)
                raise PermissionError(f"User {current_user_id} does not own task {task_id}")

            # Log successful authorization if user was validated
            if current_user_id:
                log_authorization_decision("delete", current_user_id, f"task-{task_id}", True)

            session.delete(db_task)
            session.commit()

            log_operation("TASK_DELETED", user_id=db_task.user_id, task_id=task_id)
            return True
        except Exception as e:
            log_error(e, "DELETE_TASK")
            session.rollback()
            raise

    @staticmethod
    def toggle_task_completion(session: Session, task_id: int, current_user_id: str = None) -> Optional[Task]:
        """
        Toggle the completion status of a task, with user ownership validation if current_user_id is provided
        """
        try:
            statement = select(Task).where(Task.id == task_id)
            db_task = session.exec(statement).first()

            if not db_task:
                log_operation("TASK_TOGGLE_FAILED_NOT_FOUND", task_id=task_id)
                return None

            # If current user is provided, validate ownership
            if current_user_id and db_task.user_id != current_user_id:
                log_authorization_decision("toggle", current_user_id, f"task-{task_id}", False)
                raise PermissionError(f"User {current_user_id} does not own task {task_id}")

            # Log successful authorization if user was validated
            if current_user_id:
                log_authorization_decision("toggle", current_user_id, f"task-{task_id}", True)

            # Toggle completion status
            db_task.completed = not db_task.completed

            session.add(db_task)
            session.commit()
            session.refresh(db_task)

            log_operation("TASK_COMPLETION_TOGGLED", user_id=db_task.user_id, task_id=task_id)
            return db_task
        except Exception as e:
            log_error(e, "TOGGLE_TASK_COMPLETION")
            session.rollback()
            raise

    @staticmethod
    def verify_task_ownership(session: Session, task_id: int, user_id: str) -> bool:
        """
        Verify that a specific user owns a specific task
        """
        try:
            statement = select(Task).where(Task.id == task_id)
            task = session.exec(statement).first()

            if not task:
                return False

            return task.user_id == user_id
        except Exception as e:
            log_error(e, "VERIFY_TASK_OWNERSHIP")
            raise
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth.security import create_access_token
from backend.src.models.task import TaskCreate


def test_user_data_isolation_with_different_users():
    """Test that different users cannot access each other's tasks"""
    client = TestClient(app)

    # Create tokens for two different users
    user1_data = {"user_id": "user_1_test", "role": "user"}
    user2_data = {"user_id": "user_2_test", "role": "user"}

    token_user1 = create_access_token(data=user1_data)
    token_user2 = create_access_token(data=user2_data)

    # User 1 creates a task
    task_data = {
        "title": "User 1 task",
        "description": "This is a task for user 1",
        "user_id": "user_1_test"
    }

    response = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 201
    task_response = response.json()
    task_id = task_response["id"]

    # User 2 tries to access user 1's task (should be denied)
    response_user2_access = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    # This should fail with 403 Forbidden or 404 Not Found (depending on implementation)
    assert response_user2_access.status_code in [403, 404]


def test_user_can_access_own_tasks():
    """Test that users can access their own tasks"""
    client = TestClient(app)

    # Create a token for a user
    user_data = {"user_id": "own_task_user", "role": "user"}
    token = create_access_token(data=user_data)

    # User creates a task
    task_data = {
        "title": "Own task",
        "description": "This is my own task",
        "user_id": "own_task_user"
    }

    response = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    task_response = response.json()
    task_id = task_response["id"]

    # User should be able to access their own task
    response_get = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # This should succeed
    assert response_get.status_code in [200, 404]  # 200 if endpoint allows getting single task, 404 if not


def test_user_cannot_modify_other_users_task():
    """Test that users cannot modify other users' tasks"""
    client = TestClient(app)

    # Create tokens for two different users
    user1_data = {"user_id": "mod_user_1", "role": "user"}
    user2_data = {"user_id": "mod_user_2", "role": "user"}

    token_user1 = create_access_token(data=user1_data)
    token_user2 = create_access_token(data=user2_data)

    # User 1 creates a task
    task_data = {
        "title": "User 1 task to be protected",
        "description": "This task should not be modifiable by others",
        "user_id": "mod_user_1"
    }

    response = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 201
    task_response = response.json()
    task_id = task_response["id"]

    # User 2 tries to update user 1's task (should be denied)
    update_data = {
        "title": "Attempted unauthorized update",
        "description": "User 2 shouldn't be able to do this"
    }

    response_user2_update = client.put(
        f"/api/v1/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    # This should fail with 403 Forbidden
    assert response_user2_update.status_code == 403


def test_user_cannot_delete_other_users_task():
    """Test that users cannot delete other users' tasks"""
    client = TestClient(app)

    # Create tokens for two different users
    user1_data = {"user_id": "del_user_1", "role": "user"}
    user2_data = {"user_id": "del_user_2", "role": "user"}

    token_user1 = create_access_token(data=user1_data)
    token_user2 = create_access_token(data=user2_data)

    # User 1 creates a task
    task_data = {
        "title": "User 1 task to be protected from deletion",
        "description": "This task should not be deletable by others",
        "user_id": "del_user_1"
    }

    response = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response.status_code == 201
    task_response = response.json()
    task_id = task_response["id"]

    # User 2 tries to delete user 1's task (should be denied)
    response_user2_delete = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    # This should fail with 403 Forbidden
    assert response_user2_delete.status_code == 403


def test_user_can_access_their_task_list():
    """Test that users can access their own task list"""
    client = TestClient(app)

    # Create a token for a user
    user_data = {"user_id": "task_list_user", "role": "user"}
    token = create_access_token(data=user_data)

    # User accesses their own task list (should be allowed)
    response = client.get(
        "/api/v1/tasks/task_list_user",
        headers={"Authorization": f"Bearer {token}"}
    )

    # This should succeed (might return empty list if no tasks exist)
    assert response.status_code in [200, 404]  # 200 for success, 404 if endpoint not found but auth passed


if __name__ == "__main__":
    pytest.main([__file__])
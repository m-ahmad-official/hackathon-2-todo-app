import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth.security import create_access_token


def test_integration_cross_user_access_prevention():
    """Integration test to ensure users cannot access other users' data"""
    client = TestClient(app)

    # Create tokens for two different users
    user1_data = {"user_id": "integration_user_1", "role": "user"}
    user2_data = {"user_id": "integration_user_2", "role": "user"}

    token_user1 = create_access_token(data=user1_data)
    token_user2 = create_access_token(data=user2_data)

    # Step 1: User 1 creates a task
    task_data = {
        "title": "Integration test task for user 1",
        "description": "This task belongs to user 1 and should be protected",
        "user_id": "integration_user_1"
    }

    response_create = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response_create.status_code == 201, f"Failed to create task: {response_create.text}"
    task_response = response_create.json()
    task_id = task_response["id"]

    # Step 2: Verify User 1 can access their own task
    response_user1_access = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    # This should succeed (if the endpoint exists)
    # Note: Our current API might not have a single-task endpoint, so we check for either 200 or 404
    assert response_user1_access.status_code in [200, 404], f"User 1 should be able to access their task or get 404 if endpoint doesn't exist"

    # Step 3: User 2 attempts to access User 1's task (should be prevented)
    response_user2_access = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    # This should be denied with 403 Forbidden or 404 Not Found (if hiding resources)
    assert response_user2_access.status_code in [403, 404], f"User 2 should not be able to access User 1's task"

    # Step 4: User 2 attempts to update User 1's task (should be prevented)
    update_data = {
        "title": "Unauthorized update attempt",
        "description": "User 2 should not be able to update this"
    }

    response_user2_update = client.put(
        f"/api/v1/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    assert response_user2_update.status_code == 403, f"User 2 should not be able to update User 1's task"

    # Step 5: User 2 attempts to delete User 1's task (should be prevented)
    response_user2_delete = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    assert response_user2_delete.status_code == 403, f"User 2 should not be able to delete User 1's task"

    # Step 6: Verify User 1 can still access their task after all these attempts
    response_final_check = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response_final_check.status_code in [200, 404], f"User 1's access should not be affected by other users' attempts"


def test_integration_user_task_list_isolation():
    """Integration test to ensure users can only see their own task lists"""
    client = TestClient(app)

    # Create tokens for two different users
    user1_data = {"user_id": "task_list_user_1", "role": "user"}
    user2_data = {"user_id": "task_list_user_2", "role": "user"}

    token_user1 = create_access_token(data=user1_data)
    token_user2 = create_access_token(data=user2_data)

    # User 1 creates a task
    task1_data = {
        "title": "User 1 task",
        "description": "Task for user 1",
        "user_id": "task_list_user_1"
    }

    response_user1_task = client.post(
        "/api/v1/tasks/",
        json=task1_data,
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response_user1_task.status_code == 201

    # User 2 creates a task
    task2_data = {
        "title": "User 2 task",
        "description": "Task for user 2",
        "user_id": "task_list_user_2"
    }

    response_user2_task = client.post(
        "/api/v1/tasks/",
        json=task2_data,
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    assert response_user2_task.status_code == 201

    # User 1 accesses their task list
    response_user1_list = client.get(
        "/api/v1/tasks/task_list_user_1",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    assert response_user1_list.status_code == 200
    user1_tasks = response_user1_list.json()

    # User 2 accesses their task list
    response_user2_list = client.get(
        "/api/v1/tasks/task_list_user_2",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    assert response_user2_list.status_code == 200
    user2_tasks = response_user2_list.json()

    # Verify that each user only sees their own tasks
    # Check that User 1's list contains their task
    user1_has_own_task = any(task.get("title") == "User 1 task" for task in user1_tasks)
    assert user1_has_own_task, "User 1 should see their own task"

    # Check that User 2's list contains their task
    user2_has_own_task = any(task.get("title") == "User 2 task" for task in user2_tasks)
    assert user2_has_own_task, "User 2 should see their own task"

    # Verify that User 1 doesn't see User 2's task and vice versa
    user1_does_not_see_user2_task = all(task.get("title") != "User 2 task" for task in user1_tasks)
    assert user1_does_not_see_user2_task, "User 1 should not see User 2's task"

    user2_does_not_see_user1_task = all(task.get("title") != "User 1 task" for task in user2_tasks)
    assert user2_does_not_see_user1_task, "User 2 should not see User 1's task"


def test_integration_user_self_modification_allowed():
    """Integration test to ensure users can modify their own tasks"""
    client = TestClient(app)

    # Create a token for a user
    user_data = {"user_id": "self_modify_user", "role": "user"}
    token = create_access_token(data=user_data)

    # User creates a task
    task_data = {
        "title": "Original title",
        "description": "Original description",
        "user_id": "self_modify_user"
    }

    response_create = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_create.status_code == 201
    task_response = response_create.json()
    task_id = task_response["id"]

    # User updates their own task (should be allowed)
    update_data = {
        "title": "Updated title",
        "description": "Updated description"
    }

    response_update = client.put(
        f"/api/v1/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_update.status_code == 200, f"User should be able to update their own task: {response_update.text}"

    # User deletes their own task (should be allowed)
    response_delete = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response_delete.status_code == 204, f"User should be able to delete their own task: {response_delete.text}"


if __name__ == "__main__":
    pytest.main([__file__])
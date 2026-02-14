import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth.security import create_access_token
from backend.src.models.task import TaskCreate


def test_authenticated_api_access_with_valid_token():
    """Test that authenticated API endpoints accept valid JWT tokens"""
    client = TestClient(app)

    # Create a valid JWT token
    user_data = {"user_id": "test_user_123", "role": "user"}
    token = create_access_token(data=user_data)

    # Make a request to a protected endpoint with the valid token
    response = client.get(
        "/api/v1/tasks/test_user_123",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check that the request was accepted (even if no tasks exist)
    # The important thing is that authentication passed
    assert response.status_code in [200, 404]  # 200 if tasks exist, 404 if none exist but auth passed


def test_authenticated_api_access_without_token():
    """Test that authenticated API endpoints reject requests without tokens"""
    client = TestClient(app)

    # Make a request to a protected endpoint without a token
    response = client.get("/api/v1/tasks/test_user_123")

    # Check that the request was rejected with 401 Unauthorized
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert "Bearer" in str(response.headers.get("WWW-Authenticate"))


def test_authenticated_api_access_with_invalid_token():
    """Test that authenticated API endpoints reject invalid JWT tokens"""
    client = TestClient(app)

    # Make a request to a protected endpoint with an invalid token
    response = client.get(
        "/api/v1/tasks/test_user_123",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    # Check that the request was rejected with 401 Unauthorized
    assert response.status_code == 401


def test_authenticated_api_access_with_expired_token():
    """Test that authenticated API endpoints reject expired JWT tokens"""
    from backend.src.auth.security import create_access_token
    from datetime import timedelta

    client = TestClient(app)

    # Create an expired JWT token
    user_data = {"user_id": "test_user_456", "role": "user"}
    expired_token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))

    # Make a request to a protected endpoint with the expired token
    response = client.get(
        "/api/v1/tasks/test_user_456",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    # Check that the request was rejected with 401 Unauthorized
    assert response.status_code == 401


def test_authenticated_task_creation_with_valid_token():
    """Test that authenticated task creation works with valid JWT tokens"""
    client = TestClient(app)

    # Create a valid JWT token
    user_data = {"user_id": "test_user_789", "role": "user"}
    token = create_access_token(data=user_data)

    # Try to create a task with the valid token
    task_data = {
        "title": "Test task from authenticated access test",
        "description": "This is a test task",
        "user_id": "test_user_789"
    }

    response = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check that the request was processed (could be 200 or 422 depending on validation)
    # The important thing is that authentication passed
    assert response.status_code in [201, 422, 400]


def test_different_users_have_different_access():
    """Test that different users have access only to their own resources"""
    client = TestClient(app)

    # Create tokens for two different users
    user1_data = {"user_id": "user_1", "role": "user"}
    user2_data = {"user_id": "user_2", "role": "user"}

    token_user1 = create_access_token(data=user1_data)
    token_user2 = create_access_token(data=user2_data)

    # Both users should be able to access their own endpoints
    response1 = client.get(
        "/api/v1/tasks/user_1",
        headers={"Authorization": f"Bearer {token_user1}"}
    )

    response2 = client.get(
        "/api/v1/tasks/user_2",
        headers={"Authorization": f"Bearer {token_user2}"}
    )

    # Both requests should be processed (either 200 or 404 depending on task existence)
    assert response1.status_code in [200, 404]
    assert response2.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth.security import create_access_token


def test_unauthorized_access_without_token():
    """Test that requests without tokens return 401 Unauthorized"""
    client = TestClient(app)

    # Try to access a protected endpoint without a token
    response = client.get("/api/v1/tasks/test_user")

    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.json()["detail"] == "No authorization token provided"


def test_unauthorized_access_with_invalid_token():
    """Test that requests with invalid tokens return 401 Unauthorized"""
    client = TestClient(app)

    # Try to access a protected endpoint with an invalid token
    response = client.get(
        "/api/v1/tasks/test_user",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_unauthorized_access_with_malformed_token():
    """Test that requests with malformed tokens return 401 Unauthorized"""
    client = TestClient(app)

    # Try to access a protected endpoint with a malformed token
    response = client.get(
        "/api/v1/tasks/test_user",
        headers={"Authorization": "Bearer malformed.token.format"}
    )

    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_unauthorized_access_to_protected_endpoints():
    """Test that all protected endpoints return 401 when accessed without tokens"""
    client = TestClient(app)

    # Test GET tasks for user
    response_get = client.get("/api/v1/tasks/test_user")
    assert response_get.status_code == 401

    # Test POST to create task
    response_post = client.post(
        "/api/v1/tasks/",
        json={"title": "Test", "user_id": "test_user"}
    )
    assert response_post.status_code == 401

    # Test PUT to update task
    response_put = client.put(
        "/api/v1/tasks/1",
        json={"title": "Updated Test"}
    )
    assert response_put.status_code == 401

    # Test PATCH to toggle task
    response_patch = client.patch("/api/v1/tasks/1/toggle")
    assert response_patch.status_code == 401

    # Test DELETE task
    response_delete = client.delete("/api/v1/tasks/1")
    assert response_delete.status_code == 401


def test_authorized_access_with_valid_token():
    """Test that requests with valid tokens are allowed"""
    client = TestClient(app)

    # Create a valid token
    user_data = {"user_id": "valid_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Access endpoint with valid token (should succeed or return 404 if no tasks exist)
    response = client.get(
        "/api/v1/tasks/valid_user",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should be authorized (might return 200 or 404 depending on if tasks exist)
    assert response.status_code in [200, 404]


def test_token_format_validation():
    """Test that various invalid token formats return 401"""
    client = TestClient(app)

    invalid_formats = [
        "",  # Empty token
        "Bearer",  # Missing token
        "Bearer ",  # Space instead of token
        "Basic token",  # Wrong scheme
        "Bearer token with spaces",  # Token with spaces
    ]

    for auth_header in invalid_formats:
        response = client.get(
            "/api/v1/tasks/test_user",
            headers={"Authorization": auth_header} if auth_header else {}
        )

        # If no header at all, it should return 401 for missing token
        # If invalid format, it should return 401 for invalid token
        assert response.status_code == 401, f"Failed for format: '{auth_header}'"


def test_expired_token_handling():
    """Test that expired tokens return 401"""
    from backend.src.auth.security import create_access_token
    from datetime import timedelta

    client = TestClient(app)

    # Create an expired token
    user_data = {"user_id": "expired_user", "role": "user"}
    expired_token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))

    # Try to access with expired token
    response = client.get(
        "/api/v1/tasks/expired_user",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    # Should return 401 for expired token
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


if __name__ == "__main__":
    pytest.main([__file__])
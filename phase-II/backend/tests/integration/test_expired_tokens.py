import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from jose import jwt
from backend.src.main import app
from backend.src.core.config import settings
from backend.src.auth.security import create_access_token


def test_integration_request_with_expired_token_returns_401():
    """Integration test that requests with expired tokens return 401"""
    client = TestClient(app)

    # Create an expired token manually
    expired_data = {
        "user_id": "expired_integration_user",
        "role": "user",
        "exp": 1000  # Set to Unix epoch + 1000 seconds (definitely in the past)
    }

    expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Try to access a protected endpoint with expired token
    response = client.get(
        "/api/v1/tasks/expired_integration_user",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    # Should return 401 for expired token
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.json()["detail"] == "Invalid or expired token"


def test_integration_short_lived_token_expires_during_session():
    """Integration test that short-lived tokens expire during a session"""
    client = TestClient(app)

    # Create a token with a very short lifetime
    user_data = {"user_id": "short_session_user", "role": "user"}
    short_lived_token = create_access_token(
        data=user_data,
        expires_delta=timedelta(seconds=1)
    )

    # Initially, the token should work
    response_before_expiry = client.get(
        "/api/v1/tasks/short_session_user",
        headers={"Authorization": f"Bearer {short_lived_token}"}
    )

    # Response might be 200 (success) or 404 (not found but auth passed)
    assert response_before_expiry.status_code in [200, 404]

    # Wait for the token to expire
    import time
    time.sleep(2)  # Wait for 2 seconds (longer than 1-second expiry)

    # Now the same token should fail
    response_after_expiry = client.get(
        "/api/v1/tasks/short_session_user",
        headers={"Authorization": f"Bearer {short_lived_token}"}
    )

    # Should return 401 for expired token
    assert response_after_expiry.status_code == 401


def test_integration_expired_token_on_different_endpoints():
    """Integration test that expired tokens are rejected on all endpoints"""
    client = TestClient(app)

    # Create an expired token manually
    expired_data = {
        "user_id": "multi_endpoint_user",
        "role": "user",
        "exp": 1000  # Set to definitely expired
    }

    expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Test all endpoints with expired token
    endpoints_to_test = [
        ("GET", f"/api/v1/tasks/multi_endpoint_user", {}),
        ("POST", "/api/v1/tasks/", {"json": {"title": "Test", "user_id": "multi_endpoint_user"}}),
        ("PUT", "/api/v1/tasks/1", {"json": {"title": "Updated"}}),
        ("PATCH", "/api/v1/tasks/1/toggle", {}),
        ("DELETE", "/api/v1/tasks/1", {})
    ]

    for method, endpoint, kwargs in endpoints_to_test:
        response = getattr(client, method.lower())(endpoint, headers={"Authorization": f"Bearer {expired_token}"}, **kwargs)

        # All should return 401 for expired token
        assert response.status_code == 401, f"Method {method} to {endpoint} should return 401 for expired token, got {response.status_code}"


def test_integration_token_expiry_affects_all_operations():
    """Integration test that token expiry affects all user operations consistently"""
    client = TestClient(app)

    # Create a short-lived token
    user_data = {"user_id": "consistency_user", "role": "user"}
    short_token = create_access_token(
        data=user_data,
        expires_delta=timedelta(seconds=1)
    )

    # All operations should work initially with the valid token
    initial_responses = []
    initial_responses.append(client.get(f"/api/v1/tasks/consistency_user", headers={"Authorization": f"Bearer {short_token}"}))
    initial_responses.append(client.post("/api/v1/tasks/", json={"title": "Initial", "user_id": "consistency_user"}, headers={"Authorization": f"Bearer {short_token}"}))

    # Check that initial responses are either successful or indicate auth passed
    for response in initial_responses:
        assert response.status_code in [200, 201, 404, 422], f"Initial request should succeed or reach validation, got {response.status_code}"

    # Wait for token to expire
    import time
    time.sleep(2)

    # Same operations should now fail with expired token
    expired_responses = []
    expired_responses.append(client.get(f"/api/v1/tasks/consistency_user", headers={"Authorization": f"Bearer {short_token}"}))
    expired_responses.append(client.post("/api/v1/tasks/", json={"title": "Expired", "user_id": "consistency_user"}, headers={"Authorization": f"Bearer {short_token}"}))

    # Check that all expired responses return 401
    for response in expired_responses:
        assert response.status_code == 401, f"Request with expired token should return 401, got {response.status_code}"


def test_integration_system_handles_expired_token_gracefully():
    """Integration test that the system handles expired tokens gracefully without crashing"""
    client = TestClient(app)

    # Create multiple expired tokens with different user IDs
    expired_tokens = []
    for i in range(5):
        expired_data = {
            "user_id": f"graceful_user_{i}",
            "role": "user",
            "exp": 1000  # All definitely expired
        }
        expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        expired_tokens.append(expired_token)

    # Make multiple requests with expired tokens
    for i, token in enumerate(expired_tokens):
        response = client.get(
            f"/api/v1/tasks/graceful_user_{i}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should consistently return 401 without system errors
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers


def test_integration_expired_vs_valid_token_behavior():
    """Integration test comparing behavior of expired vs valid tokens"""
    client = TestClient(app)

    # Create an expired token
    expired_data = {
        "user_id": "compare_expired_user",
        "role": "user",
        "exp": 1000  # Definitely expired
    }
    expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Create a valid token
    valid_data = {"user_id": "compare_valid_user", "role": "user"}
    valid_token = create_access_token(data=valid_data, expires_delta=timedelta(hours=1))

    # Request with expired token should return 401
    expired_response = client.get(
        "/api/v1/tasks/compare_expired_user",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert expired_response.status_code == 401

    # Request with valid token should proceed (might return 200 or 404 depending on data)
    valid_response = client.get(
        "/api/v1/tasks/compare_valid_user",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert valid_response.status_code in [200, 404], f"Valid token should allow access, got {valid_response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app


def test_integration_all_endpoints_require_authentication():
    """Integration test to ensure all protected endpoints return 401 without authentication"""
    client = TestClient(app)

    # Test GET all tasks for user without authentication
    response_get = client.get("/api/v1/tasks/test_user")
    assert response_get.status_code == 401, f"Expected 401 for GET, got {response_get.status_code}"
    assert "WWW-Authenticate" in response_get.headers
    assert "Bearer" in str(response_get.headers.get("WWW-Authenticate"))

    # Test POST to create task without authentication
    response_post = client.post(
        "/api/v1/tasks/",
        json={"title": "Test task", "user_id": "test_user"}
    )
    assert response_post.status_code == 401, f"Expected 401 for POST, got {response_post.status_code}"
    assert "WWW-Authenticate" in response_post.headers

    # Test PUT to update task without authentication
    response_put = client.put(
        "/api/v1/tasks/1",
        json={"title": "Updated task"}
    )
    assert response_put.status_code == 401, f"Expected 401 for PUT, got {response_put.status_code}"
    assert "WWW-Authenticate" in response_put.headers

    # Test PATCH to toggle task completion without authentication
    response_patch = client.patch("/api/v1/tasks/1/toggle")
    assert response_patch.status_code == 401, f"Expected 401 for PATCH, got {response_patch.status_code}"
    assert "WWW-Authenticate" in response_patch.headers

    # Test DELETE task without authentication
    response_delete = client.delete("/api/v1/tasks/1")
    assert response_delete.status_code == 401, f"Expected 401 for DELETE, got {response_delete.status_code}"
    assert "WWW-Authenticate" in response_delete.headers


def test_integration_unauthorized_requests_return_consistent_format():
    """Integration test to ensure 401 responses have consistent format"""
    client = TestClient(app)

    # Test various endpoints and verify consistent 401 response format
    endpoints_to_test = [
        ("GET", "/api/v1/tasks/test_user", {}),
        ("POST", "/api/v1/tasks/", {"json": {"title": "Test", "user_id": "test"}}),
        ("PUT", "/api/v1/tasks/1", {"json": {"title": "Updated"}}),
        ("PATCH", "/api/v1/tasks/1/toggle", {}),
        ("DELETE", "/api/v1/tasks/1", {})
    ]

    for method, endpoint, kwargs in endpoints_to_test:
        response = getattr(client, method.lower())(endpoint, **kwargs)

        assert response.status_code == 401, f"Method {method} to {endpoint} should return 401, got {response.status_code}"

        # Verify WWW-Authenticate header is present
        assert "WWW-Authenticate" in response.headers, f"Missing WWW-Authenticate header for {method} {endpoint}"
        assert "Bearer" in str(response.headers["WWW-Authenticate"]), f"Wrong authentication scheme for {method} {endpoint}"

        # Verify error response format
        error_detail = response.json()
        assert "detail" in error_detail, f"Missing detail in error response for {method} {endpoint}"
        assert isinstance(error_detail["detail"], str), f"Detail should be string for {method} {endpoint}"


def test_integration_public_endpoints_still_work():
    """Integration test to ensure public endpoints still work without authentication"""
    client = TestClient(app)

    # Test the root endpoint (should be public)
    response = client.get("/")
    assert response.status_code in [200, 404], f"Public endpoint should be accessible, got {response.status_code}"


def test_integration_multiple_unauthenticated_requests():
    """Integration test to ensure system handles multiple unauthenticated requests correctly"""
    client = TestClient(app)

    # Send multiple unauthenticated requests in sequence
    for i in range(5):
        response = client.get(f"/api/v1/tasks/test_user_{i}")
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert "Bearer" in str(response.headers["WWW-Authenticate"])


def test_integration_different_http_methods_unauthorized():
    """Integration test to ensure different HTTP methods return 401 when unauthenticated"""
    client = TestClient(app)

    # Test various HTTP methods to ensure they all require authentication
    methods_to_test = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    for method in methods_to_test:
        # Use a method-appropriate endpoint
        if method == "GET":
            response = client.get("/api/v1/tasks/test_user")
        elif method == "POST":
            response = client.post("/api/v1/tasks/", json={"title": "Test", "user_id": "test"})
        elif method == "PUT":
            response = client.put("/api/v1/tasks/1", json={"title": "Updated"})
        elif method == "PATCH":
            response = client.patch("/api/v1/tasks/1/toggle")
        elif method == "DELETE":
            response = client.delete("/api/v1/tasks/1")

        assert response.status_code == 401, f"Method {method} should return 401 when unauthenticated"
        assert "WWW-Authenticate" in response.headers, f"Method {method} missing WWW-Authenticate header"


def test_integration_error_message_consistency():
    """Integration test to ensure error messages are consistent across endpoints"""
    client = TestClient(app)

    # Test that all unauthenticated requests return the same or similar error message
    responses = []

    # Make requests to different endpoints without authentication
    responses.append(client.get("/api/v1/tasks/test_user"))
    responses.append(client.post("/api/v1/tasks/", json={"title": "Test", "user_id": "test"}))
    responses.append(client.put("/api/v1/tasks/1", json={"title": "Updated"}))

    # Check that all responses have the same status code and similar error structure
    for response in responses:
        assert response.status_code == 401
        assert "detail" in response.json()


if __name__ == "__main__":
    pytest.main([__file__])
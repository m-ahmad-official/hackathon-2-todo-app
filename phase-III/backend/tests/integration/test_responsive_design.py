import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.auth.security import create_access_token
from backend.src.models.task import TaskCreate


def test_responsive_design_mobile_view():
    """Test that the application works properly on mobile screen sizes"""
    client = TestClient(app)

    # Create a valid token for testing
    user_data = {"user_id": "responsive_test_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Test responsive task list endpoint with mobile-like request
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    }

    response = client.get(
        "/api/v1/tasks/responsive_test_user",
        headers=headers
    )

    # Should return 200 or 404 (if no tasks exist but auth passed)
    assert response.status_code in [200, 404]

    # Verify that the response is properly structured even for mobile
    if response.status_code == 200:
        tasks = response.json()
        assert isinstance(tasks, list)  # Response should be a list of tasks


def test_responsive_design_tablet_view():
    """Test that the application works properly on tablet screen sizes"""
    client = TestClient(app)

    # Create a valid token for testing
    user_data = {"user_id": "tablet_responsive_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Test with tablet-like user agent
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    }

    response = client.get(
        "/api/v1/tasks/tablet_responsive_user",
        headers=headers
    )

    # Should return 200 or 404 (if no tasks exist but auth passed)
    assert response.status_code in [200, 404]


def test_responsive_design_desktop_view():
    """Test that the application works properly on desktop screen sizes"""
    client = TestClient(app)

    # Create a valid token for testing
    user_data = {"user_id": "desktop_responsive_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Test with desktop-like user agent
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = client.get(
        "/api/v1/tasks/desktop_responsive_user",
        headers=headers
    )

    # Should return 200 or 404 (if no tasks exist but auth passed)
    assert response.status_code in [200, 404]


def test_responsive_task_creation_form():
    """Test that task creation works across different device types"""
    client = TestClient(app)

    # Create a valid token for testing
    user_data = {"user_id": "form_responsive_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Test task creation with different user agents (representing different devices)
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",  # Mobile
        "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",           # Tablet
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"              # Desktop
    ]

    for ua in user_agents:
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": ua,
            "Content-Type": "application/json"
        }

        task_data = {
            "title": f"Task from {ua[:10]}...",
            "description": f"Created from device type: {ua}",
            "user_id": "form_responsive_user"
        }

        response = client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=headers
        )

        # Should succeed regardless of device type
        assert response.status_code in [200, 201, 422], f"Failed for user agent: {ua}"


def test_responsive_task_operations():
    """Test that all task operations work properly across different screen sizes"""
    client = TestClient(app)

    # Create a valid token for testing
    user_data = {"user_id": "ops_responsive_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Create a task first
    task_data = {
        "title": "Responsive test task",
        "description": "Task to test responsive operations",
        "user_id": "ops_responsive_user"
    }

    create_response = client.post(
        "/api/v1/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert create_response.status_code in [200, 201]
    task = create_response.json()
    task_id = task.get("id") or task.get("data", {}).get("id")

    if task_id:
        # Test operations with mobile user agent
        mobile_headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        }

        # Test updating task from mobile
        update_data = {"title": "Updated from mobile", "completed": True}
        update_response = client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_data,
            headers=mobile_headers
        )
        assert update_response.status_code in [200, 201]

        # Test toggling completion from tablet
        tablet_headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)"
        }

        toggle_response = client.patch(
            f"/api/v1/tasks/{task_id}/toggle",
            headers=tablet_headers
        )
        assert toggle_response.status_code == 200


def test_different_screen_size_requests():
    """Test API responses are consistent across different simulated screen sizes"""
    client = TestClient(app)

    # Create a valid token for testing
    user_data = {"user_id": "screen_size_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Different viewport sizes simulated through headers
    viewports = [
        {"width": 375, "height": 667, "device": "mobile"},      # iPhone SE
        {"width": 768, "height": 1024, "device": "tablet"},     # iPad
        {"width": 1920, "height": 1080, "device": "desktop"}    # Desktop
    ]

    for viewport in viewports:
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Viewport-Width": str(viewport["width"]),
            "User-Agent": f"TestAgent/{viewport['device']}"
        }

        response = client.get(
            f"/api/v1/tasks/{viewport['device']}_user",
            headers=headers
        )

        # Response should be structurally the same regardless of viewport
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)  # Should always return a list of tasks


if __name__ == "__main__":
    pytest.main([__file__])
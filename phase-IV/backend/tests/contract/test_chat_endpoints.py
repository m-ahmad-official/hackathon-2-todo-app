"""
Contract tests for chat API endpoints

Tests the API contract and HTTP status codes for all chat endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.database import get_session
from backend.src.models.conversation import ConversationCreate
from backend.src.auth.security import create_access_token

# Initialize test client
client = TestClient(app)

# Test data
TEST_USER_ID = "test_user_123"
TEST_TOKEN = create_access_token(data={"user_id": TEST_USER_ID})
INVALID_TOKEN = "invalid.jwt.token"

@pytest.fixture
def cleanup_conversations():
    """Cleanup conversations after each test"""
    session = get_session()
    session.exec("DELETE FROM conversation WHERE user_id = :user_id", {"user_id": TEST_USER_ID})
    session.commit()
    session.close()

class TestChatEndpoints:
    """Test chat API endpoints contract"""

    def test_create_conversation_success(self, cleanup_conversations):
        """Test creating a conversation with valid data"""
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == TEST_USER_ID
        assert response.json()["title"] == "Test Conversation"

    def test_create_conversation_missing_title(self, cleanup_conversations):
        """Test creating a conversation with missing title"""
        response = client.post(
            "/api/v1/chat/",
            json={},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == TEST_USER_ID
        assert response.json()["title"] == None

    def test_create_conversation_invalid_token(self, cleanup_conversations):
        """Test creating a conversation with invalid token"""
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {INVALID_TOKEN}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_list_conversations_success(self, cleanup_conversations):
        """Test listing conversations with valid token"""
        # Create test data
        client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation 1"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        response = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 200
        assert len(response.json()) >= 1
        assert all(conv["user_id"] == TEST_USER_ID for conv in response.json())

    def test_list_conversations_pagination(self, cleanup_conversations):
        """Test listing conversations with pagination parameters"""
        # Create test data
        for i in range(25):
            client.post(
                "/api/v1/chat/",
                json={"title": f"Test Conversation {i}"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # Test pagination
        response = client.get(
            "/api/v1/chat/?limit=10&offset=5",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_get_conversation_success(self, cleanup_conversations):
        """Test getting a specific conversation"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Get conversation
        response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 200
        assert response.json()["id"] == conversation_id
        assert response.json()["user_id"] == TEST_USER_ID

    def test_get_conversation_not_found(self, cleanup_conversations):
        """Test getting a non-existent conversation"""
        response = client.get(
            "/api/v1/chat/999999",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_conversation_success(self, cleanup_conversations):
        """Test deleting a conversation"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Delete conversation
        response = client.delete(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 204

    def test_delete_conversation_not_found(self, cleanup_conversations):
        """Test deleting a non-existent conversation"""
        response = client.delete(
            "/api/v1/chat/999999",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_conversation_messages_success(self, cleanup_conversations):
        """Test getting messages from a conversation"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Add messages
        client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Hello", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Hi there!", "sender": "ai"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Get messages
        response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 200
        assert len(response.json()) >= 2
        assert all(msg["conversation_id"] == conversation_id for msg in response.json())

    def test_get_conversation_messages_pagination(self, cleanup_conversations):
        """Test getting messages with pagination"""
        # Create conversation and add many messages
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        for i in range(25):
            client.post(
                f"/api/v1/chat/{conversation_id}/messages",
                json={"content": f"Message {i}", "sender": "user"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # Test pagination
        response = client.get(
            f"/api/v1/chat/{conversation_id}/messages?limit=10",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_add_message_success(self, cleanup_conversations):
        """Test adding a message to a conversation"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Add message
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test message", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 201
        assert response.json()["content"] == "Test message"
        assert response.json()["sender"] == "user"
        assert response.json()["conversation_id"] == conversation_id

    def test_add_message_invalid_sender(self, cleanup_conversations):
        """Test adding a message with invalid sender"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Add message with invalid sender
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test message", "sender": "invalid"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 400
        assert "must be 'user' or 'ai'" in response.json()["detail"].lower()

    def test_add_message_missing_content(self, cleanup_conversations):
        """Test adding a message with missing content"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Add message with missing content
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 422
        assert "content" in response.json()["detail"][0]["loc"]

    def test_add_message_empty_content(self, cleanup_conversations):
        """Test adding a message with empty content"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_id = create_response.json()["id"]

        # Add message with empty content
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 422
        assert "ensure this value has at least 1 characters" in response.json()["detail"][0]["msg"]

    def test_conversation_ownership_verification(self, cleanup_conversations):
        """Test that users can only access their own conversations"""
        # Create conversation for test user
        client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Try to access with different user token
        different_user_token = create_access_token(data={"user_id": "different_user"})

        # List conversations with different user
        response = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {different_user_token}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 0  # Should not see conversations from other users

        # Try to get a specific conversation with different user
        conversations = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        ).json()

        if conversations:
            conversation_id = conversations[0]["id"]
            response = client.get(
                f"/api/v1/chat/{conversation_id}",
                headers={"Authorization": f"Bearer {different_user_token}"}
            )
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
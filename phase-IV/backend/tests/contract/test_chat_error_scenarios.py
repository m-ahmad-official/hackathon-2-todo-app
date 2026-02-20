"""
Error scenario tests for chat functionality

Tests various error conditions and edge cases for chat endpoints
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
    session.exec("DELETE FROM message WHERE conversation_id IN (SELECT id FROM conversation WHERE user_id = :user_id)", {"user_id": TEST_USER_ID})
    session.exec("DELETE FROM conversation WHERE user_id = :user_id", {"user_id": TEST_USER_ID})
    session.commit()
    session.close()

class TestChatErrorScenarios:
    """Test various error scenarios and edge cases for chat functionality"""

    def test_database_connection_error(self, cleanup_conversations):
        """Test handling of database connection errors"""
        # Create conversation should fail if database is unavailable
        with patch('backend.src.core.database.get_session', side_effect=Exception("Database connection failed")):
            response = client.post(
                "/api/v1/chat/",
                json={"title": "Test Conversation"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )
            assert response.status_code == 500
            assert "An error occurred while creating the conversation" in response.json()["detail"]

    def test_conversation_not_found(self, cleanup_conversations):
        """Test accessing non-existent conversation"""
        response = client.get(
            "/api/v1/chat/999999",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_message_not_found(self, cleanup_conversations):
        """Test accessing messages for non-existent conversation"""
        response = client.get(
            "/api/v1/chat/999999/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_missing_authorization_header(self, cleanup_conversations):
        """Test missing authorization header"""
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_invalid_authorization_header_format(self, cleanup_conversations):
        """Test invalid authorization header format"""
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": "InvalidFormat"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_empty_content_message(self, cleanup_conversations):
        """Test adding message with empty content"""
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

    def test_content_too_long(self, cleanup_conversations):
        """Test adding message with content exceeding maximum length"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Create content that exceeds 10000 characters
        long_content = "A" * 10001

        # Add message with too long content
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": long_content, "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "ensure this value has at most 10000 characters" in response.json()["detail"][0]["msg"]

    def test_invalid_sender_type(self, cleanup_conversations):
        """Test adding message with invalid sender type"""
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
            json={"content": "Test", "sender": "invalid"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 400
        assert "must be 'user' or 'ai'" in response.json()["detail"].lower()

    def test_missing_sender(self, cleanup_conversations):
        """Test adding message without sender"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add message without sender
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "sender" in response.json()["detail"][0]["loc"]

    def test_missing_content(self, cleanup_conversations):
        """Test adding message without content"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add message without content
        response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "content" in response.json()["detail"][0]["loc"]

    def test_conversation_limit_exceeded(self, cleanup_conversations):
        """Test listing conversations with limit exceeding maximum"""
        # Create many conversations
        for i in range(25):
            client.post(
                "/api/v1/chat/",
                json={"title": f"Conversation {i}"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # Try to get with limit exceeding maximum (100)
        response = client.get(
            "/api/v1/chat/?limit=101",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "ensure this value is less than or equal to 100" in response.json()["detail"][0]["msg"]

    def test_negative_limit(self, cleanup_conversations):
        """Test listing conversations with negative limit"""
        response = client.get(
            "/api/v1/chat/?limit=-1",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "ensure this value is greater than or equal to 1" in response.json()["detail"][0]["msg"]

    def test_negative_offset(self, cleanup_conversations):
        """Test listing conversations with negative offset"""
        response = client.get(
            "/api/v1/chat/?offset=-1",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "ensure this value is greater than or equal to 0" in response.json()["detail"][0]["msg"]

    def test_zero_limit(self, cleanup_conversations):
        """Test listing conversations with zero limit"""
        response = client.get(
            "/api/v1/chat/?limit=0",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "ensure this value is greater than or equal to 1" in response.json()["detail"][0]["msg"]

    def test_invalid_query_parameters(self, cleanup_conversations):
        """Test invalid query parameters"""
        response = client.get(
            "/api/v1/chat/?invalid_param=value",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "extra fields not permitted" in response.json()["detail"][0]["msg"]

    def test_empty_database(self, cleanup_conversations):
        """Test behavior when database is empty"""
        # List conversations when none exist
        response = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Try to get non-existent conversation
        response = client.get(
            "/api/v1/chat/1",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 404

    def test_conversation_ownership_violation(self, cleanup_conversations):
        """Test trying to access conversations from another user"""
        # Create conversation for test user
        client.post(
            "/api/v1/chat/",
            json={"title": "Test User Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Create conversation for different user
        different_user_token = create_access_token(data={"user_id": "different_user"})
        different_user_response = client.post(
            "/api/v1/chat/",
            json={"title": "Different User Conversation"},
            headers={"Authorization": f"Bearer {different_user_token}"}
        )
        different_user_conversation_id = different_user_response.json()["id"]

        # Try to access different user's conversation
        response = client.get(
            f"/api/v1/chat/{different_user_conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Try to add message to different user's conversation
        response = client.post(
            f"/api/v1/chat/{different_user_conversation_id}/messages",
            json={"content": "Test", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Try to delete different user's conversation
        response = client.delete(
            f"/api/v1/chat/{different_user_conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_concurrent_access(self, cleanup_conversations):
        """Test concurrent access scenarios"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Concurrent Test"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Simulate concurrent message addition
        response1 = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Message 1", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        response2 = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Message 2", "sender": "ai"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response1.status_code == 201
        assert response2.status_code == 201

        # Verify both messages are present
        messages_response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert messages_response.status_code == 200
        messages = messages_response.json()
        assert len(messages) == 2
        assert any(msg["content"] == "Message 1" and msg["sender"] == "user" for msg in messages)
        assert any(msg["content"] == "Message 2" and msg["sender"] == "ai" for msg in messages)

    def test_empty_string_title(self, cleanup_conversations):
        """Test creating conversation with empty string title"""
        response = client.post(
            "/api/v1/chat/",
            json={"title": ""},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == ""  # Empty string should be preserved

    def test_whitespace_title(self, cleanup_conversations):
        """Test creating conversation with whitespace title"""
        response = client.post(
            "/api/v1/chat/",
            json={"title": "   "},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "   "  # Whitespace should be preserved

    def test_null_title(self, cleanup_conversations):
        """Test creating conversation without title (null)"""
        response = client.post(
            "/api/v1/chat/",
            json={},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == None  # No title should be null

    def test_special_characters_title(self, cleanup_conversations):
        """Test creating conversation with special characters in title"""
        special_title = "Test & Conversation !@#$%^&*()_+-=[]{}|;:'\",./<>?"
        response = client.post(
            "/api/v1/chat/",
            json={"title": special_title},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == special_title

    def test_unicode_title(self, cleanup_conversations):
        """Test creating conversation with unicode characters in title"""
        unicode_title = "你好，世界! 😊"  # "Hello, World! 😊"
        response = client.post(
            "/api/v1/chat/",
            json={"title": unicode_title},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == unicode_title

    def test_max_length_title(self, cleanup_conversations):
        """Test creating conversation with maximum length title"""
        max_title = "A" * 200  # Maximum length is 200
        response = client.post(
            "/api/v1/chat/",
            json={"title": max_title},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == max_title

    def test_over_max_length_title(self, cleanup_conversations):
        """Test creating conversation with title exceeding maximum length"""
        over_max_title = "A" * 201  # Exceeds maximum length of 200
        response = client.post(
            "/api/v1/chat/",
            json={"title": over_max_title},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 422
        assert "ensure this value has at most 200 characters" in response.json()["detail"][0]["msg"]

    def test_invalid_content_type(self, cleanup_conversations):
        """Test invalid content type in request"""
        response = client.post(
            "/api/v1/chat/",
            data="title=Test Conversation",
            headers={"Authorization": f"Bearer {TEST_TOKEN}", "Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422
        assert "invalid character '=' looking for beginning of value" in response.json()["detail"]

    def test_large_number_of_conversations(self, cleanup_conversations):
        """Test performance with large number of conversations"""
        # Create 1000 conversations
        for i in range(1000):
            client.post(
                "/api/v1/chat/",
                json={"title": f"Conversation {i}"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # List conversations with pagination
        response = client.get(
            "/api/v1/chat/?limit=100&offset=900",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 100  # Should return 100 conversations from offset 900
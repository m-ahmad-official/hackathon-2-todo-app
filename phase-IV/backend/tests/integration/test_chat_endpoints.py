"""
Integration tests for chat endpoints
"""

import pytest
import httpx
from backend.src.models.conversation import ConversationCreate
from backend.src.models.message import Message

BASE_URL = "http://localhost:8000"


class TestChatEndpoints:
    """Integration tests for chat endpoints"""

    @pytest.fixture
    async def setup_conversation(self, auth_client):
        """Create a conversation for testing"""
        conversation_data = ConversationCreate(title="Test Conversation")
        response = await auth_client.post("/api/v1/chat/", json=conversation_data.dict())
        assert response.status_code == 201
        return response.json()

    async def test_create_conversation(self, auth_client):
        """Test creating a new conversation"""
        # Test with title
        conversation_data = ConversationCreate(title="Test Conversation")
        response = await auth_client.post("/api/v1/chat/", json=conversation_data.dict())

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["user_id"] == auth_client.user_id
        assert "id" in data

        # Test without title
        response = await auth_client.post("/api/v1/chat/", json={})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] is None

    async def test_list_conversations(self, auth_client, setup_conversation):
        """Test listing conversations"""
        # Create multiple conversations
        for i in range(3):
            await auth_client.post("/api/v1/chat/", json={"title": f"Conversation {i}".})

        # Test listing with default parameters
        response = await auth_client.get("/api/v1/chat/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # Should return all 3 conversations
        assert all(conv["user_id"] == auth_client.user_id for conv in data)

        # Test pagination
        response = await auth_client.get("/api/v1/chat/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Test offset
        response = await auth_client.get("/api/v1/chat/?limit=1&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    async def test_get_conversation(self, auth_client, setup_conversation):
        """Test getting a specific conversation"""
        conversation_id = setup_conversation["id"]

        # Test getting existing conversation
        response = await auth_client.get(f"/api/v1/chat/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conversation_id
        assert data["title"] == "Test Conversation"

        # Test getting non-existent conversation
        response = await auth_client.get("/api/v1/chat/99999")
        assert response.status_code == 404

    async def test_delete_conversation(self, auth_client, setup_conversation):
        """Test deleting a conversation"""
        conversation_id = setup_conversation["id"]

        # Test deleting existing conversation
        response = await auth_client.delete(f"/api/v1/chat/{conversation_id}")
        assert response.status_code == 204

        # Test getting deleted conversation (should return 404)
        response = await auth_client.get(f"/api/v1/chat/{conversation_id}")
        assert response.status_code == 404

        # Test deleting non-existent conversation
        response = await auth_client.delete("/api/v1/chat/99999")
        assert response.status_code == 404

    async def test_get_conversation_messages(self, auth_client, setup_conversation):
        """Test getting messages from a conversation"""
        conversation_id = setup_conversation["id"]

        # Test getting messages from empty conversation
        response = await auth_client.get(f"/api/v1/chat/{conversation_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        # Test getting messages with limit
        response = await auth_client.get(f"/api/v1/chat/{conversation_id}/messages?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_add_message(self, auth_client, setup_conversation):
        """Test adding messages to a conversation"""
        conversation_id = setup_conversation["id"]

        # Test adding valid message (user)
        message_data = {
            "content": "Hello, this is a test message!",
            "sender": "user"
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, this is a test message!"
        assert data["sender"] == "user"
        assert data["conversation_id"] == conversation_id

        # Test adding valid message (ai)
        message_data = {
            "content": "Hello! How can I help you today?",
            "sender": "ai"
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello! How can I help you today?"
        assert data["sender"] == "ai"

        # Test invalid sender
        message_data = {
            "content": "Invalid sender test",
            "sender": "invalid"
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 400

        # Test missing required fields
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json={})
        assert response.status_code == 422

    async def test_cross_user_access(self, auth_client, auth_client_2):
        """Test that users can only access their own conversations"""
        # Create conversation with first user
        conversation_data = ConversationCreate(title="Private Conversation")
        response = await auth_client.post("/api/v1/chat/", json=conversation_data.dict())
        assert response.status_code == 201
        conversation = response.json()

        # Second user should not be able to access first user's conversation
        response = await auth_client_2.get(f"/api/v1/chat/{conversation[\"id\"]}")
        assert response.status_code == 404

        # Second user should not be able to delete first user's conversation
        response = await auth_client_2.delete(f"/api/v1/chat/{conversation[\"id\"]}")
        assert response.status_code == 404

    async def test_message_limits(self, auth_client, setup_conversation):
        """Test message limits and validation"""
        conversation_id = setup_conversation["id"]

        # Test message length limits
        long_message = "A" * 10000  # Max length
        message_data = {
            "content": long_message,
            "sender": "user"
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 201

        # Test message that's too long
        too_long_message = "A" * 10001
        message_data = {
            "content": too_long_message,
            "sender": "user"
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 422

    async def test_metadata_support(self, auth_client, setup_conversation):
        """Test message metadata support"""
        conversation_id = setup_conversation["id"]

        # Test adding message with metadata
        message_data = {
            "content": "Test message with metadata",
            "sender": "user",
            "metadata": {
                "timestamp": "2024-01-01T12:00:00Z",
                "source": "test",
                "confidence": 0.95
            }
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"] == message_data["metadata"]

        # Test adding message without metadata
        message_data = {
            "content": "Test message without metadata",
            "sender": "user"
        }
        response = await auth_client.post(f"/api/v1/chat/{conversation_id}/messages", json=message_data)
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"] is None


# Required fixtures for authentication
@pytest.fixture
async def auth_client():
    """Authenticated client for testing"""
    from backend.src.auth.security import create_access_token
    from backend.src.auth.deps import ALGORITHM

    # Create test user
    user_id = "test_user_123"
    token = create_access_token(data={"sub": user_id}, algorithm=ALGORITHM)

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        client.user_id = user_id
        yield client


@pytest.fixture
async def auth_client_2():
    """Second authenticated client for testing"""
    from backend.src.auth.security import create_access_token
    from backend.src.auth.deps import ALGORITHM

    # Create second test user
    user_id = "test_user_456"
    token = create_access_token(data={"sub": user_id}, algorithm=ALGORITHM)

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        client.user_id = user_id
        yield client
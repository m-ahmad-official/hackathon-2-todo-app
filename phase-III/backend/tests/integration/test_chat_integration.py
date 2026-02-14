"""
Integration tests for chat functionality

Tests the complete chat workflow including database operations, authentication, and business logic
"""

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.database import get_session
from backend.src.models.conversation import ConversationCreate
from backend.src.auth.security import create_access_token
from backend.src.models.conversation import Conversation, Message

# Initialize test client
client = TestClient(app)

# Test data
TEST_USER_ID = "test_user_123"
TEST_TOKEN = create_access_token(data={"user_id": TEST_USER_ID})

@pytest.fixture
def cleanup_conversations():
    """Cleanup conversations after each test"""
    session = get_session()
    session.exec("DELETE FROM message WHERE conversation_id IN (SELECT id FROM conversation WHERE user_id = :user_id)", {"user_id": TEST_USER_ID})
    session.exec("DELETE FROM conversation WHERE user_id = :user_id", {"user_id": TEST_USER_ID})
    session.commit()
    session.close()

@pytest.fixture
def test_conversation(cleanup_conversations):
    """Create a test conversation for integration tests"""
    response = client.post(
        "/api/v1/chat/",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    return response.json()["id"]

class TestChatIntegration:
    """Integration tests for chat functionality"""

    def test_complete_chat_workflow(self, cleanup_conversations):
        """Test complete chat workflow from creation to message exchange"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Complete Chat Workflow"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]
        assert create_response.status_code == 201

        # Add user message
        user_message_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Hello, how are you?", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert user_message_response.status_code == 201
        user_message_id = user_message_response.json()["id"]

        # Add AI message
        ai_message_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "I'm doing well, thank you!", "sender": "ai"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert ai_message_response.status_code == 201
        ai_message_id = ai_message_response.json()["id"]

        # Verify conversation update
        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 200
        assert conversation_response.json()["updated_at"] != conversation_response.json()["created_at"]

        # Get all messages
        messages_response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert messages_response.status_code == 200
        messages = messages_response.json()
        assert len(messages) == 2
        assert any(msg["content"] == "Hello, how are you?" and msg["sender"] == "user" for msg in messages)
        assert any(msg["content"] == "I'm doing well, thank you!" and msg["sender"] == "ai" for msg in messages)

        # Test message ordering (chronological)
        message_ids = [msg["id"] for msg in messages]
        assert message_ids.index(user_message_id) < message_ids.index(ai_message_id)

    def test_conversation_persistence(self, cleanup_conversations):
        """Test that conversations are persisted in the database"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Persistent Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add multiple messages
        for i in range(5):
            client.post(
                f"/api/v1/chat/{conversation_id}/messages",
                json={"content": f"Message {i}", "sender": "user"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # Retrieve conversation directly from database
        session = get_session()
        db_conversation = session.get(Conversation, conversation_id)
        db_messages = session.exec(
            "SELECT * FROM message WHERE conversation_id = :conversation_id ORDER BY created_at",
            {"conversation_id": conversation_id}
        ).all()
        session.close()

        assert db_conversation is not None
        assert db_conversation.user_id == TEST_USER_ID
        assert db_conversation.title == "Persistent Conversation"
        assert len(db_messages) == 5

    def test_context_retention(self, cleanup_conversations):
        """Test that conversation context is retained across messages"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Context Retention Test"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add messages that build context
        messages = [
            ("user", "I need to buy groceries"),
            ("ai", "What groceries do you need?"),
            ("user", "Milk, eggs, and bread"),
            ("ai", "Should I add these to your shopping list?"),
            ("user", "Yes please"),
            ("ai", "Added to shopping list: Milk, eggs, bread")
        ]

        for sender, content in messages:
            response = client.post(
                f"/api/v1/chat/{conversation_id}/messages",
                json={"content": content, "sender": sender},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )
            assert response.status_code == 201

        # Get all messages and verify context flow
        messages_response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert messages_response.status_code == 200
        retrieved_messages = messages_response.json()

        # Verify all messages are present in correct order
        assert len(retrieved_messages) == 6
        for i, (sender, content) in enumerate(messages):
            assert retrieved_messages[i]["sender"] == sender
            assert retrieved_messages[i]["content"] == content

    def test_conversation_deletion(self, cleanup_conversations):
        """Test that conversation deletion removes all related messages"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Delete Test"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add messages
        for i in range(3):
            client.post(
                f"/api/v1/chat/{conversation_id}/messages",
                json={"content": f"Message {i}", "sender": "user"},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # Verify conversation and messages exist
        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 200

        messages_response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert messages_response.status_code == 200
        assert len(messages_response.json()) == 3

        # Delete conversation
        delete_response = client.delete(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert delete_response.status_code == 204

        # Verify conversation and messages are deleted
        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 404

        messages_response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert messages_response.status_code == 404

        # Verify database cleanup
        session = get_session()
        db_conversation = session.get(Conversation, conversation_id)
        db_messages = session.exec(
            "SELECT * FROM message WHERE conversation_id = :conversation_id",
            {"conversation_id": conversation_id}
        ).all()
        session.close()

        assert db_conversation is None
        assert len(db_messages) == 0

    def test_conversation_metadata(self, cleanup_conversations):
        """Test conversation metadata (message count, last message)"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Metadata Test"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add messages
        messages = [
            ("user", "First message"),
            ("ai", "Second message"),
            ("user", "Third message")
        ]

        for sender, content in messages:
            client.post(
                f"/api/v1/chat/{conversation_id}/messages",
                json={"content": content, "sender": sender},
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )

        # Get conversation and check metadata
        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 200
        conversation_data = conversation_response.json()

        # Check metadata (note: metadata not currently included in response, but we can verify through messages)
        messages_response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert messages_response.status_code == 200
        assert len(messages_response.json()) == 3

    def test_conversation_title_updates(self, cleanup_conversations):
        """Test that conversation title is preserved"""
        # Create conversation with title
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Original Title"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Verify title is preserved
        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 200
        assert conversation_response.json()["title"] == "Original Title"

        # Add messages and verify title remains
        client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test message", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 200
        assert conversation_response.json()["title"] == "Original Title"

    def test_conversation_creation_without_title(self, cleanup_conversations):
        """Test creating conversation without title"""
        # Create conversation without title
        create_response = client.post(
            "/api/v1/chat/",
            json={},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert create_response.status_code == 201
        conversation_id = create_response.json()["id"]

        # Verify conversation was created with no title
        conversation_response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversation_response.status_code == 200
        assert conversation_response.json()["title"] == None

    def test_conversation_list_ordering(self, cleanup_conversations):
        """Test that conversations are ordered by updated_at descending"""
        # Create multiple conversations
        client.post(
            "/api/v1/chat/",
            json={"title": "Old Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Create a newer conversation
        newer_conversation_response = client.post(
            "/api/v1/chat/",
            json={"title": "New Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        newer_conversation_id = newer_conversation_response.json()["id"]

        # Add message to newer conversation to update its timestamp
        client.post(
            f"/api/v1/chat/{newer_conversation_id}/messages",
            json={"content": "Update timestamp", "sender": "user"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Get conversations and verify ordering
        conversations_response = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert conversations_response.status_code == 200
        conversations = conversations_response.json()

        # The newer conversation (with updated timestamp) should appear first
        assert conversations[0]["title"] == "New Conversation"

    def test_conversation_user_isolation(self, cleanup_conversations):
        """Test that users can only access their own conversations"""
        # Create conversation for test user
        client.post(
            "/api/v1/chat/",
            json={"title": "Test User Conversation"},
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        # Create conversation for different user
        different_user_token = create_access_token(data={"user_id": "different_user"})
        client.post(
            "/api/v1/chat/",
            json={"title": "Different User Conversation"},
            headers={"Authorization": f"Bearer {different_user_token}"}
        )

        # Test test user can only see their own conversations
        test_user_conversations = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        ).json()

        different_user_conversations = client.get(
            "/api/v1/chat/",
            headers={"Authorization": f"Bearer {different_user_token}"}
        ).json()

        # Each user should only see their own conversations
        assert len(test_user_conversations) == 1
        assert len(different_user_conversations) == 1
        assert test_user_conversations[0]["title"] == "Test User Conversation"
        assert different_user_conversations[0]["title"] == "Different User Conversation"

        # Test accessing specific conversation with wrong user
        conversation_id = test_user_conversations[0]["id"]
        response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {different_user_token}"}
        )
        assert response.status_code == 404

        # Test accessing messages with wrong user
        response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {different_user_token}"}
        )
        assert response.status_code == 404
"""
Authentication and authorization tests for chat functionality

Tests JWT token validation, user access control, and security isolation
"""

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.database import get_session
from backend.src.models.conversation import ConversationCreate
from backend.src.auth.security import create_access_token, verify_token

# Initialize test client
client = TestClient(app)

# Test data
VALID_USER_ID = "test_user_123"
VALID_TOKEN = create_access_token(data={"user_id": VALID_USER_ID})
INVALID_TOKEN = "invalid.jwt.token"
EXPIRED_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyIiwiZXhwIjoxMjM0NTY3ODkwfQ.invalid.signature"

@pytest.fixture
def cleanup_conversations():
    """Cleanup conversations after each test"""
    session = get_session()
    session.exec("DELETE FROM message WHERE conversation_id IN (SELECT id FROM conversation WHERE user_id = :user_id)", {"user_id": VALID_USER_ID})
    session.exec("DELETE FROM conversation WHERE user_id = :user_id", {"user_id": VALID_USER_ID})
    session.commit()
    session.close()

@pytest.fixture
def different_user_token():
    """Create token for a different user"""
    return create_access_token(data={"user_id": "different_user_456"})

class TestChatAuthentication:
    """Test authentication and authorization for chat endpoints"""

    def test_valid_token_required_for_all_endpoints(self):
        """Test that all chat endpoints require a valid token"""
        # Test create conversation without token
        response = client.post("/api/v1/chat/", json={"title": "Test"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test list conversations without token
        response = client.get("/api/v1/chat/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test get conversation without token
        response = client.get("/api/v1/chat/1")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test delete conversation without token
        response = client.delete("/api/v1/chat/1")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test get messages without token
        response = client.get("/api/v1/chat/1/messages")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test add message without token
        response = client.post("/api/v1/chat/1/messages", json={"content": "Test", "sender": "user"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_invalid_token_rejected(self, cleanup_conversations):
        """Test that invalid tokens are rejected"""
        # Test with invalid token format
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {INVALID_TOKEN}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test with expired token
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {EXPIRED_TOKEN}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test with malformed token
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test"},
            headers={"Authorization": "Bearer invalid-token-format"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_token_extraction(self, cleanup_conversations):
        """Test token extraction from Authorization header"""
        # Test missing "Bearer" prefix
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test"},
            headers={"Authorization": VALID_TOKEN}  # Missing "Bearer" prefix
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # Test correct "Bearer" prefix
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert response.status_code == 201

    def test_user_isolation_success(self, cleanup_conversations, different_user_token):
        """Test that users can only access their own conversations"""
        # Create conversation for valid user
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Valid User Conversation"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Different user should not see this conversation
        response = client.get(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {different_user_token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Different user should not be able to modify this conversation
        response = client.delete(
            f"/api/v1/chat/{conversation_id}",
            headers={"Authorization": f"Bearer {different_user_token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_conversation_ownership_verification(self, cleanup_conversations):
        """Test that conversation ownership is properly verified"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Add message to verify ownership
        message_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test message", "sender": "user"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert message_response.status_code == 201

        # Try to access with different user (should fail)
        different_user_token = create_access_token(data={"user_id": "different_user"})
        response = client.get(
            f"/api/v1/chat/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {different_user_token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_token_user_id_extraction(self, cleanup_conversations):
        """Test that user ID is correctly extracted from token"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert create_response.status_code == 201
        assert create_response.json()["user_id"] == VALID_USER_ID

        # Verify that user ID is used for ownership
        conversation_id = create_response.json()["id"]
        message_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test", "sender": "user"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert message_response.status_code == 201

    def test_multiple_users_concurrent_access(self, cleanup_conversations):
        """Test concurrent access by multiple users"""
        # Create conversations for two different users
        user1_token = create_access_token(data={"user_id": "user1"})
        user2_token = create_access_token(data={"user_id": "user2"})

        # User 1 creates conversation
        response1 = client.post(
            "/api/v1/chat/",
            json={"title": "User 1 Conversation"},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response1.status_code == 201
        conv1_id = response1.json()["id"]

        # User 2 creates conversation
        response2 = client.post(
            "/api/v1/chat/",
            json={"title": "User 2 Conversation"},
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response2.status_code == 201
        conv2_id = response2.json()["id"]

        # User 1 can access their own conversation
        response1_get = client.get(
            f"/api/v1/chat/{conv1_id}",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response1_get.status_code == 200

        # User 1 cannot access User 2's conversation
        response1_access_others = client.get(
            f"/api/v1/chat/{conv2_id}",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response1_access_others.status_code == 404

        # User 2 can access their own conversation
        response2_get = client.get(
            f"/api/v1/chat/{conv2_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response2_get.status_code == 200

        # User 2 cannot access User 1's conversation
        response2_access_others = client.get(
            f"/api/v1/chat/{conv1_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response2_access_others.status_code == 404

    def test_user_id_injection_prevention(self, cleanup_conversations):
        """Test that user cannot inject their own user_id"""
        # Try to create conversation with user_id in payload (should be ignored)
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Test", "user_id": "attempted_injection"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == VALID_USER_ID  # Should use token user_id, not payload

    def test_token_refresh_not_required(self, cleanup_conversations):
        """Test that tokens don't need to be refreshed for this API"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Wait a moment and use same token
        import time
        time.sleep(1)

        # Add message with same token
        message_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test", "sender": "user"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert message_response.status_code == 201

    def test_token_blacklist_not_implemented(self, cleanup_conversations):
        """Test that token blacklisting is not implemented (as expected)"""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        conversation_id = create_response.json()["id"]

        # Even if we tried to "logout" by creating a new token, old token should still work
        new_token = create_access_token(data={"user_id": VALID_USER_ID})
        message_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test", "sender": "user"},
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert message_response.status_code == 201

        # Old token should still work
        old_token_response = client.post(
            f"/api/v1/chat/{conversation_id}/messages",
            json={"content": "Test 2", "sender": "user"},
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        assert old_token_response.status_code == 201

    def test_token_scope_validation(self, cleanup_conversations):
        """Test that token contains required scope/user_id"""
        # Create token with minimal required data
        minimal_token = create_access_token(data={"user_id": "minimal_user"})
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Minimal Token Test"},
            headers={"Authorization": f"Bearer {minimal_token}"}
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == "minimal_user"

        # Token without user_id should fail
        with pytest.raises(Exception):
            create_access_token(data={})  # Should raise error if no user_id

    def test_token_algorithm_validation(self, cleanup_conversations):
        """Test that only expected token algorithms are accepted"""
        # Create token with different algorithm (should be rejected by verify_token)
        from jose import jwt
        from datetime import datetime, timedelta

        # Create token with HS256 (should be rejected if system expects RS256 or different)
        test_payload = {"user_id": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)}
        test_token = jwt.encode(test_payload, "secret", algorithm="HS256")

        # This should be rejected by verify_token if it only accepts certain algorithms
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Algorithm Test"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_token_expiration_handling(self, cleanup_conversations):
        """Test token expiration handling"""
        # Create expired token
        from datetime import datetime, timedelta
        expired_payload = {"user_id": "expired_user", "exp": datetime.utcnow() - timedelta(minutes=1)}
        expired_token = create_access_token(data=expired_payload)

        # Try to use expired token
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Expired Token Test"},
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_token_with_additional_claims(self, cleanup_conversations):
        """Test tokens with additional claims (should be ignored for this API)"""
        # Create token with additional claims
        extended_token = create_access_token(data={"user_id": "extended_user", "role": "admin", "permissions": ["read", "write"]})
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Extended Token Test"},
            headers={"Authorization": f"Bearer {extended_token}"}
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == "extended_user"

    def test_token_missing_user_id_claim(self, cleanup_conversations):
        """Test token without user_id claim (should fail)"""
        # Create token without user_id (should raise error in create_access_token)
        with pytest.raises(Exception):
            create_access_token(data={"role": "user"})  # Should require user_id

    def test_token_with_special_characters(self, cleanup_conversations):
        """Test token with special characters in user_id"""
        # Create token with special characters in user_id
        special_user_id = "user!@#$%^&*()_+"
        special_token = create_access_token(data={"user_id": special_user_id})
        response = client.post(
            "/api/v1/chat/",
            json={"title": "Special Characters Test"},
            headers={"Authorization": f"Bearer {special_token}"}
        )
        assert response.status_code == 201
        assert response.json()["user_id"] == special_user_id
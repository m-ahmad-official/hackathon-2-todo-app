"""
Unit tests for conversation service

Tests the conversation service business logic in isolation
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation
from src.models.message import Message

class TestConversationService:
    """Unit tests for ConversationService"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        return MagicMock()

    @pytest.fixture
    def test_conversation(self):
        """Create a test conversation object"""
        return Conversation(
            id=1,
            user_id="test_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            title="Test Conversation"
        )

    @pytest.fixture
    def test_message(self):
        """Create a test message object"""
        return Message(
            id=1,
            conversation_id=1,
            content="Test message",
            sender="user",
            created_at=datetime.utcnow()
        )

    def test_create_conversation_success(self, mock_session):
        """Test creating a conversation successfully"""
        # Setup
        service = ConversationService()
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Execute
        conversation = service.create_conversation(mock_session, "test_user", "Test Title")

        # Verify
        assert conversation.user_id == "test_user"
        assert conversation.title == "Test Title"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    def test_create_conversation_without_title(self, mock_session):
        """Test creating a conversation without title"""
        # Setup
        service = ConversationService()
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Execute
        conversation = service.create_conversation(mock_session, "test_user")

        # Verify
        assert conversation.user_id == "test_user"
        assert conversation.title == None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    def test_get_conversation_success(self, mock_session, test_conversation):
        """Test getting an existing conversation"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.first.return_value = test_conversation

        # Execute
        conversation = service.get_conversation(mock_session, 1, "test_user")

        # Verify
        assert conversation == test_conversation
        mock_session.exec.assert_called_once()

    def test_get_conversation_not_found(self, mock_session):
        """Test getting a non-existent conversation"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.first.return_value = None

        # Execute
        conversation = service.get_conversation(mock_session, 999, "test_user")

        # Verify
        assert conversation == None
        mock_session.exec.assert_called_once()

    def test_get_conversation_wrong_user(self, mock_session):
        """Test getting a conversation with wrong user"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.first.return_value = None

        # Execute
        conversation = service.get_conversation(mock_session, 1, "wrong_user")

        # Verify
        assert conversation == None
        mock_session.exec.assert_called_once()

    def test_list_conversations_success(self, mock_session):
        """Test listing conversations successfully"""
        # Setup
        service = ConversationService()
        test_conversations = [
            Conversation(id=1, user_id="test_user", title="C1"),
            Conversation(id=2, user_id="test_user", title="C2")
        ]
        mock_session.exec.return_value.all.return_value = test_conversations

        # Execute
        conversations = service.list_conversations(mock_session, "test_user", limit=10, offset=0)

        # Verify
        assert len(conversations) == 2
        assert all(conv.user_id == "test_user" for conv in conversations)
        mock_session.exec.assert_called_once()

    def test_list_conversations_empty(self, mock_session):
        """Test listing conversations when none exist"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.all.return_value = []

        # Execute
        conversations = service.list_conversations(mock_session, "test_user", limit=10, offset=0)

        # Verify
        assert len(conversations) == 0
        mock_session.exec.assert_called_once()

    def test_delete_conversation_success(self, mock_session, test_conversation):
        """Test deleting an existing conversation"""
        # Setup
        service = ConversationService()
        mock_session.get.return_value = test_conversation
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Execute
        result = service.delete_conversation(mock_session, 1, "test_user")

        # Verify
        assert result == True
        mock_session.get.assert_called_once_with(Conversation, 1)
        mock_session.delete.assert_called_once_with(test_conversation)
        mock_session.commit.assert_called_once()

    def test_delete_conversation_not_found(self, mock_session):
        """Test deleting a non-existent conversation"""
        # Setup
        service = ConversationService()
        mock_session.get.return_value = None
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Execute
        result = service.delete_conversation(mock_session, 999, "test_user")

        # Verify
        assert result == False
        mock_session.get.assert_called_once_with(Conversation, 999)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_delete_conversation_wrong_user(self, mock_session):
        """Test deleting a conversation with wrong user"""
        # Setup
        service = ConversationService()
        mock_session.get.return_value = None  # Will return None due to user mismatch
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        # Execute
        result = service.delete_conversation(mock_session, 1, "wrong_user")

        # Verify
        assert result == False
        mock_session.get.assert_called_once_with(Conversation, 1)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_add_message_success(self, mock_session, test_conversation):
        """Test adding a message successfully"""
        # Setup
        service = ConversationService()
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        mock_session.get.return_value = test_conversation

        # Execute
        message = service.add_message(
            mock_session,
            conversation_id=1,
            content="Test message",
            sender="user",
            metadata={"key": "value"}
        )

        # Verify
        assert message.conversation_id == 1
        assert message.content == "Test message"
        assert message.sender == "user"
        assert message.metadata == {"key": "value"}
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called()
        mock_session.refresh.assert_called_once()
        mock_session.get.assert_called_once_with(Conversation, 1)

    def test_add_message_without_metadata(self, mock_session, test_conversation):
        """Test adding a message without metadata"""
        # Setup
        service = ConversationService()
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        mock_session.get.return_value = test_conversation

        # Execute
        message = service.add_message(
            mock_session,
            conversation_id=1,
            content="Test message",
            sender="user"
        )

        # Verify
        assert message.conversation_id == 1
        assert message.content == "Test message"
        assert message.sender == "user"
        assert message.metadata == None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called()
        mock_session.refresh.assert_called_once()

    def test_get_conversation_messages_success(self, mock_session):
        """Test getting conversation messages successfully"""
        # Setup
        service = ConversationService()
        test_messages = [
            Message(id=1, conversation_id=1, content="Msg1", sender="user"),
            Message(id=2, conversation_id=1, content="Msg2", sender="ai")
        ]
        mock_session.exec.return_value.all.return_value = test_messages

        # Execute
        messages = service.get_conversation_messages(mock_session, conversation_id=1, limit=10)

        # Verify
        assert len(messages) == 2
        assert all(msg.conversation_id == 1 for msg in messages)
        mock_session.exec.assert_called_once()

    def test_get_conversation_messages_empty(self, mock_session):
        """Test getting conversation messages when none exist"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.all.return_value = []

        # Execute
        messages = service.get_conversation_messages(mock_session, conversation_id=1, limit=10)

        # Verify
        assert len(messages) == 0
        mock_session.exec.assert_called_once()

    def test_get_recent_messages_success(self, mock_session):
        """Test getting recent messages successfully"""
        # Setup
        service = ConversationService()
        test_messages = [
            Message(id=1, conversation_id=1, content="Old", sender="user", created_at=datetime(2023, 1, 1)),
            Message(id=2, conversation_id=1, content="New", sender="ai", created_at=datetime(2023, 1, 2))
        ]
        mock_session.exec.return_value.all.return_value = test_messages

        # Execute
        messages = service.get_recent_messages(mock_session, conversation_id=1, limit=10)

        # Verify
        assert len(messages) == 2
        assert messages[0].content == "New"  # Newest first
        assert messages[1].content == "Old"
        mock_session.exec.assert_called_once()

    def test_get_conversation_metadata_success(self, mock_session, test_conversation, test_message):
        """Test getting conversation metadata"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.first.side_effect = [test_conversation, test_message]
        mock_session.exec.return_value.count.return_value = 1

        # Execute
        metadata = service.get_conversation_metadata(mock_session, conversation_id=1, user_id="test_user")

        # Verify
        assert metadata is not None
        assert metadata["conversation"] == test_conversation
        assert metadata["message_count"] == 1
        assert metadata["last_message"] == test_message
        assert mock_session.exec.call_count == 3  # 3 queries executed

    def test_get_conversation_metadata_not_found(self, mock_session):
        """Test getting conversation metadata for non-existent conversation"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.first.return_value = None

        # Execute
        metadata = service.get_conversation_metadata(mock_session, conversation_id=999, user_id="test_user")

        # Verify
        assert metadata == None
        mock_session.exec.assert_called_once()

    def test_get_conversation_metadata_wrong_user(self, mock_session):
        """Test getting conversation metadata with wrong user"""
        # Setup
        service = ConversationService()
        mock_session.exec.return_value.first.return_value = None

        # Execute
        metadata = service.get_conversation_metadata(mock_session, conversation_id=1, user_id="wrong_user")

        # Verify
        assert metadata == None
        mock_session.exec.assert_called_once()

    def test_update_conversation_timestamp(self, mock_session, test_conversation):
        """Test that adding a message updates conversation timestamp"""
        # Setup
        service = ConversationService()
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        mock_session.get.return_value = test_conversation

        # Execute
        service.add_message(
            mock_session,
            conversation_id=1,
            content="Test message",
            sender="user"
        )

        # Verify timestamp update
        assert test_conversation.updated_at != test_conversation.created_at
        mock_session.commit.assert_called()  # Should be called twice: once for message, once for update

    def test_message_ordering_chronological(self, mock_session):
        """Test that messages are returned in chronological order"""
        # Setup
        service = ConversationService()
        test_messages = [
            Message(id=1, conversation_id=1, content="Msg1", sender="user", created_at=datetime(2023, 1, 1, 10, 0)),
            Message(id=2, conversation_id=1, content="Msg2", sender="ai", created_at=datetime(2023, 1, 1, 11, 0)),
            Message(id=3, conversation_id=1, content="Msg3", sender="user", created_at=datetime(2023, 1, 1, 9, 0))
        ]
        mock_session.exec.return_value.all.return_value = test_messages

        # Execute
        messages = service.get_conversation_messages(mock_session, conversation_id=1, limit=10)

        # Verify ordering
        assert messages[0].content == "Msg3"  # Oldest first
        assert messages[1].content == "Msg1"
        assert messages[2].content == "Msg2"
        mock_session.exec.assert_called_once()

    def test_message_limit(self, mock_session):
        """Test message limit functionality"""
        # Setup
        service = ConversationService()
        test_messages = [
            Message(id=i, conversation_id=1, content=f"Msg{i}", sender="user")
            for i in range(1, 6)
        ]
        mock_session.exec.return_value.all.return_value = test_messages

        # Execute with limit 3
        messages = service.get_conversation_messages(mock_session, conversation_id=1, limit=3)

        # Verify
        assert len(messages) == 3
        mock_session.exec.assert_called_once()

    def test_message_offset(self, mock_session):
        """Test message offset functionality"""
        # Setup
        service = ConversationService()
        test_messages = [
            Message(id=i, conversation_id=1, content=f"Msg{i}", sender="user")
            for i in range(1, 6)
        ]
        mock_session.exec.return_value.all.return_value = test_messages

        # Execute with offset 2
        messages = service.get_conversation_messages(mock_session, conversation_id=1, limit=10, offset=2)

        # Verify
        assert len(messages) == 3  # Only 3 messages left after offset
        mock_session.exec.assert_called_once()

    def test_invalid_sender_validation(self):
        """Test that invalid sender raises appropriate exception"""
        # Setup
        service = ConversationService()
        mock_session = MagicMock()
        mock_session.get.return_value = MagicMock()

        # Execute with invalid sender
        with pytest.raises(HTTPException) as exc_info:
            service.add_message(
                mock_session,
                conversation_id=1,
                content="Test message",
                sender="invalid_sender"
            )

        # Verify
        assert exc_info.value.status_code == 400
        assert "Sender must be 'user' or 'ai'" in str(exc_info.value.detail)
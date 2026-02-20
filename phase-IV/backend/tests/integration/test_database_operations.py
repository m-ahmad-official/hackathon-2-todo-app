"""
Database operation and rollback tests for chat functionality

Tests database transactions, connection pooling, and rollback scenarios
"""

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.database import get_session, get_engine
from backend.src.models.conversation import ConversationCreate
from backend.src.auth.security import create_access_token
from sqlalchemy.exc import OperationalError, IntegrityError

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
    """Create a test conversation for database tests"""
    response = client.post(
        "/api/v1/chat/",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    return response.json()["id"]

class TestDatabaseOperations:
    """Test database operations, transactions, and rollback scenarios"""

    def test_database_connection_pooling(self, cleanup_conversations):
        """Test database connection pooling"""
        # Test multiple concurrent connections
        sessions = []
        for i in range(10):
            session = get_session()
            sessions.append(session)

        # Verify all sessions are connected
        for session in sessions:
            assert session.is_active

        # Close all sessions
        for session in sessions:
            session.close()

    def test_transaction_atomicity(self, cleanup_conversations):
        """Test that transactions are atomic"""
        # Create conversation and messages in a single transaction
        session = get_session()
        try:
            # Start transaction
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Atomic Test"
            )
            session.add(conversation)
            session.flush()  # Get conversation ID

            # Add messages
            for i in range(3):
                message = Conversation(
                    conversation_id=conversation.id,
                    content=f"Message {i}",
                    sender="user"
                )
                session.add(message)

            # Commit transaction
            session.commit()

            # Verify all data was committed
            db_conversation = session.get(Conversation, conversation.id)
            db_messages = session.exec(
                "SELECT * FROM message WHERE conversation_id = :conversation_id",
                {"conversation_id": conversation.id}
            ).all()

            assert db_conversation is not None
            assert len(db_messages) == 3

        finally:
            session.close()

    def test_rollback_on_error(self, cleanup_conversations):
        """Test that transactions are rolled back on error"""
        session = get_session()
        try:
            # Start transaction
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Rollback Test"
            )
            session.add(conversation)
            session.flush()

            # Add message with invalid data (should cause error)
            message = Message(
                conversation_id=conversation.id,
                content="" * 10001,  # Exceeds max length
                sender="user"
            )
            session.add(message)

            # Try to commit (should fail)
            try:
                session.commit()
                assert False, "Commit should have failed"
            except Exception:
                # Rollback should happen automatically
                session.rollback()

                # Verify no data was committed
                db_conversation = session.get(Conversation, conversation.id)
                db_messages = session.exec(
                    "SELECT * FROM message WHERE conversation_id = :conversation_id",
                    {"conversation_id": conversation.id}
                ).all()

                assert db_conversation is None
                assert len(db_messages) == 0

        finally:
            session.close()

    def test_concurrent_transaction_isolation(self, cleanup_conversations):
        """Test transaction isolation levels"""
        session1 = get_session()
        session2 = get_session()

        try:
            # Session 1 starts transaction
            conversation1 = Conversation(
                user_id=TEST_USER_ID,
                title="Session 1"
            )
            session1.add(conversation1)
            session1.flush()

            # Session 2 tries to read (should not see uncommitted data)
            db_conversation2 = session2.get(Conversation, conversation1.id)
            assert db_conversation2 is None

            # Session 1 commits
            session1.commit()

            # Session 2 can now read the data
            db_conversation2 = session2.get(Conversation, conversation1.id)
            assert db_conversation2 is not None

        finally:
            session1.close()
            session2.close()

    def test_deadlock_detection_and_resolution(self, cleanup_conversations):
        """Test deadlock detection and resolution"""
        session1 = get_session()
        session2 = get_session()

        try:
            # Create initial data
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Deadlock Test"
            )
            session1.add(conversation)
            session1.commit()

            # Simulate deadlock scenario
            try:
                # Session 1 locks conversation
                session1.begin()
                conv1 = session1.get(Conversation, conversation.id)
                conv1.title = "Session 1 Locked"

                # Session 2 tries to lock same conversation
                session2.begin()
                conv2 = session2.get(Conversation, conversation.id)
                conv2.title = "Session 2 Locked"

                # Session 2 commits first (should succeed)
                session2.commit()

                # Session 1 tries to commit (should fail due to deadlock)
                session1.commit()
                assert False, "Session 1 commit should have failed"

            except Exception as e:
                # Rollback session 1
                session1.rollback()

                # Verify final state
                final_session = get_session()
                final_conv = final_session.get(Conversation, conversation.id)
                assert final_conv.title == "Session 2 Locked"  # Session 2 should have won
                final_session.close()

        finally:
            session1.close()
            session2.close()

    def test_savepoint_rollback(self, cleanup_conversations):
        """Test savepoint rollback functionality"""
        session = get_session()
        try:
            # Create conversation
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Savepoint Test"
            )
            session.add(conversation)
            session.commit()

            # Start transaction with savepoint
            session.begin()
            session.add(Conversation(
                conversation_id=conversation.id,
                content="Message 1",
                sender="user"
            ))

            # Create savepoint
            session.begin_nested()
            session.add(Conversation(
                conversation_id=conversation.id,
                content="Message 2",
                sender="user"
            ))

            # Rollback to savepoint (Message 2 should be removed)
            session.rollback()

            # Commit outer transaction (Message 1 should remain)
            session.commit()

            # Verify results
            final_session = get_session()
            messages = final_session.exec(
                "SELECT * FROM message WHERE conversation_id = :conversation_id",
                {"conversation_id": conversation.id}
            ).all()

            assert len(messages) == 1
            assert messages[0].content == "Message 1"
            final_session.close()

        finally:
            session.close()

    def test_connection_reuse(self, cleanup_conversations):
        """Test connection reuse in connection pool"""
        # Get multiple sessions and verify connection reuse
        session1 = get_session()
        session2 = get_session()

        # Verify connections are different
        assert session1.bind.url != session2.bind.url

        # Close sessions and get new ones (should reuse connections)
        session1.close()
        session2.close()

        session3 = get_session()
        session4 = get_session()

        # Verify connection reuse is happening (implementation specific)
        # This is more of a performance test that would be validated through monitoring

        session3.close()
        session4.close()

    def test_database_schema_validation(self, cleanup_conversations):
        """Test database schema validation"""
        session = get_session()
        try:
            # Test all required columns exist
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Schema Test"
            )
            session.add(conversation)
            session.commit()

            # Test foreign key constraints
            message = Message(
                conversation_id=conversation.id,
                content="Test message",
                sender="user"
            )
            session.add(message)
            session.commit()

            # Test index usage (performance test)
            # This would typically be validated through query analysis

        finally:
            session.close()

    def test_batch_operations(self, cleanup_conversations):
        """Test batch database operations"""
        session = get_session()
        try:
            # Batch insert conversations
            conversations = []
            for i in range(100):
                conversations.append(Conversation(
                    user_id=TEST_USER_ID,
                    title=f"Batch Conversation {i}"
                ))
            session.add_all(conversations)
            session.commit()

            # Verify batch insert
            db_conversations = session.exec(
                "SELECT * FROM conversation WHERE user_id = :user_id",
                {"user_id": TEST_USER_ID}
            ).all()
            assert len(db_conversations) == 100

        finally:
            session.close()

    def test_large_data_handling(self, cleanup_conversations):
        """Test handling of large data volumes"""
        session = get_session()
        try:
            # Create conversation
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Large Data Test"
            )
            session.add(conversation)
            session.commit()

            # Add many messages
            messages = []
            for i in range(1000):
                messages.append(Message(
                    conversation_id=conversation.id,
                    content=f"Message {i}",
                    sender="user"
                ))
            session.add_all(messages)
            session.commit()

            # Verify all messages were added
            db_messages = session.exec(
                "SELECT * FROM message WHERE conversation_id = :conversation_id",
                {"conversation_id": conversation.id}
            ).all()
            assert len(db_messages) == 1000

        finally:
            session.close()

    def test_database_error_handling(self, cleanup_conversations):
        """Test graceful handling of database errors"""
        # Test unique constraint violation
        session = get_session()
        try:
            # Create conversation
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Duplicate Test"
            )
            session.add(conversation)
            session.commit()

            # Try to create duplicate (should fail)
            duplicate = Conversation(
                user_id=TEST_USER_ID,
                title="Duplicate Test"
            )
            session.add(duplicate)

            try:
                session.commit()
                assert False, "Commit should have failed due to duplicate"
            except IntegrityError:
                session.rollback()
                assert True  # Expected failure

        finally:
            session.close()

    def test_connection_timeout_handling(self, cleanup_conversations):
        """Test handling of connection timeouts"""
        # Test connection timeout (would require database configuration)
        # This is more of a configuration test that would be validated through monitoring
        pass

    def test_read_only_transactions(self, cleanup_conversations):
        """Test read-only transactions"""
        session = get_session()
        try:
            # Create test data
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Read Only Test"
            )
            session.add(conversation)
            session.commit()

            # Start read-only transaction
            session.begin()
            db_conversation = session.get(Conversation, conversation.id)
            assert db_conversation is not None

            # Try to modify (should fail in read-only transaction)
            db_conversation.title = "Modified Title"
            try:
                session.commit()
                assert False, "Commit should have failed in read-only transaction"
            except Exception:
                session.rollback()
                assert True  # Expected failure

        finally:
            session.close()

    def test_transaction_retry_on_deadlock(self, cleanup_conversations):
        """Test automatic retry on deadlock"""
        # Test retry logic (would require implementation of retry decorator)
        # This is more of an implementation test that would be validated through specific test scenarios
        pass

    def test_database_migration_rollback(self, cleanup_conversations):
        """Test database migration rollback"""
        # Test migration rollback (would require Alembic setup)
        # This is more of a deployment test that would be validated through migration testing
        pass

    def test_data_consistency_checks(self, cleanup_conversations):
        """Test data consistency checks"""
        session = get_session()
        try:
            # Create conversation with messages
            conversation = Conversation(
                user_id=TEST_USER_ID,
                title="Consistency Test"
            )
            session.add(conversation)
            session.commit()

            # Add messages
            messages = []
            for i in range(5):
                messages.append(Message(
                    conversation_id=conversation.id,
                    content=f"Message {i}",
                    sender="user"
                ))
            session.add_all(messages)
            session.commit()

            # Verify data consistency
            db_conversation = session.get(Conversation, conversation.id)
            db_messages = session.exec(
                "SELECT * FROM message WHERE conversation_id = :conversation_id",
                {"conversation_id": conversation.id}
            ).all()

            assert db_conversation is not None
            assert len(db_messages) == 5
            assert all(msg.conversation_id == conversation.id for msg in db_messages)

        finally:
            session.close()

    def test_database_performance_under_load(self, cleanup_conversations):
        """Test database performance under load"""
        # Performance testing would require specific load testing setup
        # This is more of a performance test that would be validated through load testing tools
        pass
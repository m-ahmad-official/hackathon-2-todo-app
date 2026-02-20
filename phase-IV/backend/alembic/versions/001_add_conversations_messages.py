"""Add conversations and messages tables

Revision ID: 001_add_conversations_messages
Revises:
Create Date: 2026-02-08 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_add_conversations_messages'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade database schema."""
    # Create conversations table
    op.create_table(
        'conversation',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('title', sa.String(200), nullable=True)
    )

    # Create messages table
    op.create_table(
        'message',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('conversation_id', sa.Integer, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('sender', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ondelete='CASCADE'),
        sa.CheckConstraint("sender IN ('user', 'ai')", name='check_sender_type')
    )

    # Create indexes for performance
    op.create_index('idx_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('idx_conversation_created_at', 'conversation', ['created_at'])
    op.create_index('idx_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('idx_message_created_at', 'message', ['created_at'])
    op.create_index('idx_message_conversation_created', 'message', ['conversation_id', 'created_at'])

    # Create trigger to update conversation timestamp on new message
    op.execute("")
    op.execute("")

def downgrade():
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index('idx_message_conversation_created', table_name='message')
    op.drop_index('idx_message_created_at', table_name='message')
    op.drop_index('idx_message_conversation_id', table_name='message')
    op.drop_index('idx_conversation_created_at', table_name='conversation')
    op.drop_index('idx_conversation_user_id', table_name='conversation')

    # Drop tables
    op.drop_table('message')
    op.drop_table('conversation')
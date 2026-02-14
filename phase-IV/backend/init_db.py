"""
Initialize the database tables for the Todo API
"""
from sqlmodel import SQLModel
from src.core.database import engine
from src.models.task import Task
from src.models.user import User


def create_tables():
    """
    Create all database tables
    """
    print("Creating database tables...")

    # Create all tables defined in SQLModel metadata
    SQLModel.metadata.create_all(engine)

    print("✅ Database tables created successfully!")
    print("- Task table created")
    print("- User table created")


if __name__ == "__main__":
    create_tables()
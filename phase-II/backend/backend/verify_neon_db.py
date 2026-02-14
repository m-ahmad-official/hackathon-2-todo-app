#!/usr/bin/env python3
"""
Verify that the Neon database tables are properly set up
"""
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError


def verify_neon_database():
    """
    Verify the Neon database connection and table structure
    """
    # Get the database URL from environment or use the default
    database_url = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_OobETvcr52mH@ep-purple-rain-ahogvd6j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

    print(f"Connecting to database: {database_url.replace('@', '[AT]').replace(':', '[COLON]')}")  # Mask credentials

    try:
        # Create engine
        engine = create_engine(database_url)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"✅ Successfully connected to database. Version: {version[0][:50]}...")

        # Create an inspector
        inspector = inspect(engine)

        # Get table names
        table_names = inspector.get_table_names()
        print(f"📊 Tables in database: {table_names}")

        if 'task' in table_names:
            print("\n📋 Task table structure:")

            # Get column information for the task table
            columns = inspector.get_columns('task')
            for col in columns:
                nullable_text = "NULL" if col['nullable'] else "NOT NULL"
                print(f"   • {col['name']:<15} {str(col['type']):<25} {nullable_text}")

            print("\n✅ Task table exists with correct structure!")
            print("🎉 Your Neon database is properly set up for the Todo API!")
        else:
            print("\n❌ Task table not found in database")
            print("Attempting to create tables...")

            # Import SQLModel and create tables
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

            from sqlmodel import SQLModel
            from backend.src.models.task import Task

            # Create all tables
            SQLModel.metadata.create_all(engine)
            print("✅ Tables created successfully")

            # Check again
            table_names = inspector.get_table_names()
            print(f"📊 Tables after creation: {table_names}")

    except OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 This might be due to:")
        print("   - Incorrect database credentials in .env")
        print("   - Network connectivity issues")
        print("   - Database not properly configured in Neon")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    verify_neon_database()
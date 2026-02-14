"""
Check if the tables were created in the Neon database
"""
import os
import sys

# Add the current directory and backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel

# Import after setting up the path
from backend.src.models.task import Task


def check_tables():
    """
    Check what tables exist in the database
    """
    print("Checking database tables...")

    # Get the database URL from environment or use the default
    database_url = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_OobETvcr52mH@ep-purple-rain-ahogvd6j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

    print(f"Connecting to database: {database_url}")

    # Create engine
    engine = create_engine(database_url)

    # Create an inspector
    inspector = inspect(engine)

    # Get table names
    table_names = inspector.get_table_names()

    print(f"Tables found in database: {table_names}")

    if table_names:
        for table_name in table_names:
            print(f"\nColumns in '{table_name}' table:")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  - {col['name']} ({col['type']}) {col['nullable'] and 'NULL' or 'NOT NULL'}")
    else:
        print("❌ No tables found in the database")

    # Try to create the tables directly using SQLModel metadata
    print("\nTrying to create tables using SQLModel...")
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ Attempted to create tables via SQLModel")

        # Check again after attempting to create
        table_names = inspector.get_table_names()
        print(f"Tables found after creation attempt: {table_names}")

        if table_names:
            print("\n✅ Success! Tables have been created in your Neon database.")
            print("You can now use the Todo API to perform CRUD operations on tasks.")
        else:
            print("\n⚠️  Tables may not have been created. Please check your Neon database connection.")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")


if __name__ == "__main__":
    check_tables()
"""
Check if the tables were created in the database
"""
from sqlalchemy import inspect
from src.core.database import engine


def check_tables():
    """
    Check what tables exist in the database
    """
    print("Checking database tables...")

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


if __name__ == "__main__":
    check_tables()
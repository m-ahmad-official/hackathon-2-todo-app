from sqlmodel import create_engine, Session, SQLModel
from src.core.config import settings
from src.models.task import Task  # Import models to register them with SQLModel metadata
from src.models.user import User  # Import models to register them with SQLModel metadata

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    ),
)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

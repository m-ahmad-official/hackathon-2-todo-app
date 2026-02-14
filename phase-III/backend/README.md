# Todo API Backend

This is the backend service for the Todo application, built with FastAPI and SQLModel.

## Features

- Create, Read, Update, Delete (CRUD) operations for tasks
- User-specific task isolation
- RESTful API endpoints
- Data validation and error handling
- Logging for operations

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Validation**: Pydantic
- **Testing**: pytest

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

## Running the Application

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Endpoints

For detailed API documentation, see [docs/api-reference.md](docs/api-reference.md).

## Project Structure

```
backend/
├── src/
│   ├── main.py           # Application entry point
│   ├── models/           # SQLModel data models
│   ├── api/              # API route definitions
│   ├── core/             # Core utilities (config, database)
│   └── services/         # Business logic services
├── tests/                # Unit and integration tests
├── docs/                 # Documentation
├── alembic/              # Database migrations
├── requirements.txt      # Dependencies
└── .env.example          # Environment variables template
```

## Testing

Run the tests using pytest:

```bash
cd backend
pytest
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize the values as needed.
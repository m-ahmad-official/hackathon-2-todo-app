from fastapi import FastAPI
from src.api.v1 import tasks
from src.api.v1.auth import router as auth_router
from src.auth.middleware import JWTMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import create_db_and_tables


app = FastAPI(title="Todo API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Add JWT authentication middleware
app.add_middleware(JWTMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

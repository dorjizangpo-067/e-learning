from contextlib import asynccontextmanager
from fastapi import FastAPI

from course import router as course_router
from subscription import router as subscription_router
from user import router as user_router
from db_models import Base
from database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    Handles startup and shutdown events. Creates database tables on startup.

    :param app: The FastAPI application instance
    :type app: FastAPI
    """
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup if needed (e.g., close connections)


app = FastAPI(
    title="E-Learning for STEM Subjects - Bhutan",
    description="API for managing e-learning courses in STEM subjects for Bhutanese students.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routes
app.include_router(course_router)
app.include_router(subscription_router)
app.include_router(user_router)


@app.get("/", tags=["Home"])
async def home() -> dict:
    return {"message": "Welcome to E-Learning Waktsa Bak"}




import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test database URL before importing app
os.environ["DB_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from main import app
from db_models import Base
from database import SessionLocal

# Use file-based SQLite for tests to avoid threading issues
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Define get_db for override
def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override get_db for tests
app.dependency_overrides[get_db] = get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Tables are already created at import time
    yield
    # Drop tables and remove file after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    # Force close any remaining connections
    import gc
    gc.collect()
    import os
    import time
    if os.path.exists("./test.db"):
        # Try to remove the file, with retries in case it's still locked
        for _ in range(5):
            try:
                os.remove("./test.db")
                break
            except PermissionError:
                time.sleep(0.1)  # Wait a bit and try again

@pytest.mark.asyncio
async def test_home():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

@pytest.mark.asyncio
async def test_register_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        user_data = {
            "name": "Admin User",
            "email": "admin@example.com",
            "password": "adminpass",
            "role": "admin"
        }
        response = await client.post("/user/register", json=user_data)
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_register_student():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        user_data = {
            "name": "Student User",
            "email": "student@example.com",
            "password": "studentpass",
            "role": "student"
        }
        response = await client.post("/user/register", json=user_data)
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_register_second_admin_fails():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        user_data = {
            "name": "Another Admin",
            "email": "admin2@example.com",
            "password": "adminpass",
            "role": "admin"
        }
        response = await client.post("/user/register", json=user_data)
        assert response.status_code == 400
        assert "Admin user already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        login_data = {
            "email": "admin@example.com",
            "password": "adminpass"
        }
        response = await client.post("/user/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "access_token" in response.cookies

@pytest.mark.asyncio
async def test_login_student():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        login_data = {
            "email": "student@example.com",
            "password": "studentpass"
        }
        response = await client.post("/user/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_add_course_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as admin first
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        course_data = {
            "title": "Test Course",
            "description": "Test Description",
            "author": "Test Author",
            "course_url": "https://example.com",
            "category": "math",
            "grade": 10
        }
        response = await client.post("/course/add", json=course_data, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_courses_without_subscription():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as student
        login_data = {"email": "student@example.com", "password": "studentpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        response = await client.get("/course", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403
        assert "Subscription required" in response.json()["detail"]

@pytest.mark.asyncio
async def test_purchase_subscription():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as admin
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        # Get student id (assuming id=2)
        response = await client.post("/subscription/purchase/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "Subscription purchased" in response.json()["message"]

@pytest.mark.asyncio
async def test_get_courses_with_subscription():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as student
        login_data = {"email": "student@example.com", "password": "studentpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        response = await client.get("/course", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_filter_courses():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as student
        login_data = {"email": "student@example.com", "password": "studentpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        response = await client.get("/course/math", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_course_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as admin
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        update_data = {
            "title": "Updated Course",
            "description": "Updated Description",
            "author": "Updated Author",
            "course_url": "https://updated.com",
            "category": "science",
            "grade": 12
        }
        response = await client.put("/course/update/1", json=update_data, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Course"

@pytest.mark.asyncio
async def test_delete_course_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as admin
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        response = await client.delete("/course/delete/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "Course removed" in response.json()["message"]

@pytest.mark.asyncio
async def test_get_all_users_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as admin
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        response = await client.get("/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert len(response.json()) >= 2  # admin and student

@pytest.mark.asyncio
async def test_check_subscription_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login as admin
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        login_response = await client.post("/user/login", json=login_data)
        token = login_response.json()["access_token"]

        response = await client.get("/subscription/check/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "subscribed" in response.json()

@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Login first
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        await client.post("/user/login", json=login_data)

        response = await client.post("/user/logout")
        assert response.status_code == 200
        assert "Logged out" in response.json()["message"]
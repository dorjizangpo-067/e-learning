from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from db_models import Student
from models import StudentModel, StudentResponse, LoginModel

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    """
    Provides a database session dependency for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/student/register", tags=["User"], response_model=StudentResponse)
async def register_student(student: StudentModel, db: Session = Depends(get_db)) -> StudentResponse:
    """
    Registers a new student in the database.

    :param student: Student registration data
    :param db: Database session
    :return: The registered student
    """
    # Check if email already exists
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists"
        )

    hashed_password = pwd_context.hash(student.password)
    new_student = Student(
        name=student.name,
        email=student.email,
        hashed_password=hashed_password,
        subscribed=False,
        subscription_date=None
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.post("/student/login", tags=["User"])
async def login_student(login: LoginModel, db: Session = Depends(get_db)):
    """
    Authenticates a student by checking email and password.

    :param login: Login credentials
    :param db: Database session
    :return: Success message if authenticated
    """
    student = db.query(Student).filter(Student.email == login.email).first()
    if not student or not pwd_context.verify(login.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return {"message": "Login successful"}
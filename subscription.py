from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from database import SessionLocal
from db_models import Student
from models import StudentModel, StudentResponse

router = APIRouter()

# Common price for subscription (in Bhutanese Ngultrum or any currency)
SUBSCRIPTION_PRICE = 100.0  # Example price, can be modified
SUBSCRIPTION_DURATION_DAYS = 30


def get_db():
    """
    Provides a database session dependency for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/student/register", tags=["Subscription"], response_model=StudentResponse)
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

    new_student = Student(
        name=student.name,
        email=student.email,
        subscribed=False,
        subscription_date=None
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.post("/subscription/purchase/{student_id}", tags=["Subscription"])
async def purchase_subscription(student_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Purchases a subscription for a student. Sets subscribed to True and records the date.

    :param student_id: ID of the student
    :param db: Database session
    :return: Success message with subscription details
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Set subscription
    student.subscribed = True
    student.subscription_date = datetime.utcnow()
    db.commit()
    db.refresh(student)

    return {
        "message": "Subscription purchased successfully",
        "student_id": student.id,
        "subscription_date": student.subscription_date,
        "expires_on": student.subscription_date + timedelta(days=SUBSCRIPTION_DURATION_DAYS),
        "price": SUBSCRIPTION_PRICE
    }


@router.get("/subscription/check/{student_id}", tags=["Subscription"])
async def check_subscription(student_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Checks if a student's subscription is active (within 30 days).

    :param student_id: ID of the student
    :param db: Database session
    :return: Subscription status
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    if not student.subscribed or not student.subscription_date:
        return {"subscribed": False, "message": "No active subscription"}

    # Check if within 30 days
    expires_on = student.subscription_date + timedelta(days=SUBSCRIPTION_DURATION_DAYS)
    if datetime.utcnow() > expires_on:
        # Optionally, set subscribed to False if expired
        student.subscribed = False
        db.commit()
        return {"subscribed": False, "message": "Subscription expired"}

    return {
        "subscribed": True,
        "subscription_date": student.subscription_date,
        "expires_on": expires_on,
        "days_left": (expires_on - datetime.utcnow()).days
    }


@router.get("/students", tags=["Subscription"], response_model=list[StudentResponse])
async def get_all_students(db: Session = Depends(get_db)) -> list[StudentResponse]:
    """
    Retrieves all students (for admin purposes).

    :param db: Database session
    :return: List of all students
    """
    students = db.query(Student).all()
    return students
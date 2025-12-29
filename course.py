from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Generator
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from database import SessionLocal
from models import CourseModel, ResponseCourse
from db_models import Course, User
from jwt_setup import check_token

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session dependency for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_subscribed_user(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Dependency to get current user from JWT and verify subscription.
    
    :param request: FastAPI Request object
    :param db: Database session
    :return: User data dict if subscribed and valid
    """
    token_data = check_token(request)
    user_email = token_data["user"]["email"]
    
    # Fetch current user data from database
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.subscribed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription required to access courses"
        )
    
    subscription_date_str = user.subscription_date
    if subscription_date_str:
        expires_on = subscription_date_str + timedelta(days=30)
        if datetime.utcnow() > expires_on:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription has expired"
            )
    else:
        # If no subscription_date but subscribed=True, assume valid (maybe lifetime)
        pass
    
    return {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "subscribed": user.subscribed,
        "subscription_date": user.subscription_date.isoformat() if user.subscription_date else None
    }


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Dependency to get current user and verify they are admin.
    
    :param request: FastAPI Request object
    :param db: Database session
    :return: User data dict if admin
    """
    token_data = check_token(request)
    user_email = token_data["user"]["email"]
    
    # Fetch current user data from database
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "subscribed": user.subscribed,
        "subscription_date": user.subscription_date.isoformat() if user.subscription_date else None
    }


# Get all courses
@router.get("/course", tags=["Course"], response_model=List[ResponseCourse])
async def get_course(
    current_user: dict = Depends(get_current_subscribed_user),
    db: Session = Depends(get_db)
) -> List[ResponseCourse]:
    """
    Retrieves all courses from the database if student is subscribed.

    :param current_user: Current authenticated and subscribed user
    :param db: Database session
    :return: List of all courses
    """
    courses = db.query(Course).all()
    return courses


# Add Course
@router.post("/course/add", tags=["Course"], response_model=ResponseCourse)
async def add_course(
    course_form: CourseModel,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> ResponseCourse:
    """
    Adds a new course to the database. Admin only.

    :param course_form: Course data to be added
    :param current_admin: Current admin user
    :param db: Database session
    :return: The created course
    """
    new_course = Course(**course_form.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


# Update course
@router.put("/course/update/{course_id}", tags=["Course"], response_model=ResponseCourse)
async def update_course(
    course_id: int,
    update_course_form: CourseModel,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> ResponseCourse:
    """
    Updates an existing course in the database. Admin only.

    :param course_id: ID of the course to update
    :param update_course_form: Updated course data
    :param current_admin: Current admin user
    :param db: Database session
    :return: The updated course
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    # Verify the course exists
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The course with id={course_id} does not exist"
        )

    # Extract update data as a dict
    course_update = update_course_form.model_dump(exclude_unset=True)
    # Apply changes to the model instance
    for key, value in course_update.items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


# Delete Course
@router.delete("/course/delete/{course_id}", tags=["Course"])
async def delete_course(
    course_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict:
    """
    Deletes a course from the database. Admin only.

    :param course_id: ID of the course to delete
    :param current_admin: Current admin user
    :param db: Database session
    :return: Success message
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    db.delete(course)
    db.commit()
    return {"message": "Course removed"}


# Filter courses by grade or category
@router.get("/course/{query}", tags=["Course"], response_model=List[ResponseCourse])
async def filter_course(
    query: str,
    current_user: dict = Depends(get_current_subscribed_user),
    db: Session = Depends(get_db)
) -> List[ResponseCourse]:
    """
    Filters courses by category or grade based on the query if student is subscribed.

    :param query: Category (math, science, ict) or grade (6, 10, 12)
    :param current_user: Current authenticated and subscribed user
    :param db: Database session
    :return: List of filtered courses
    """
    query_lower = query.lower()
    if query_lower in ["math", "science", "ict"]:
        courses = db.query(Course).filter(Course.category == query_lower).all()
    elif query in ["6", "10", "12"]:
        courses = db.query(Course).filter(Course.grade == int(query)).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category or grade"
        )
    return courses
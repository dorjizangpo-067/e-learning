from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Generator
from sqlalchemy.orm import Session

from database import SessionLocal
from models import CourseModel, ResponseCourse
from db_models import Course

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


# Get all courses
@router.get("/course", tags=["Course"], response_model=List[ResponseCourse])
async def get_course(db: Session = Depends(get_db)) -> List[ResponseCourse]:
    """
    Retrieves all courses from the database.

    :param db: Database session
    :return: List of all courses
    """
    courses = db.query(Course).all()
    return courses


# Add Course
@router.post("/course/add", tags=["Course"], response_model=ResponseCourse)
async def add_course(
    course_form: CourseModel, db: Session = Depends(get_db)
) -> ResponseCourse:
    """
    Adds a new course to the database.

    :param course_form: Course data to be added
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
    db: Session = Depends(get_db)
) -> ResponseCourse:
    """
    Updates an existing course in the database.

    :param course_id: ID of the course to update
    :param update_course_form: Updated course data
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
async def delete_course(course_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Deletes a course from the database.

    :param course_id: ID of the course to delete
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
async def filter_course(query: str, db: Session = Depends(get_db)) -> List[ResponseCourse]:
    """
    Filters courses by category or grade based on the query.

    :param query: Category (math, science, ict) or grade (6, 10, 12)
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
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from database import SessionLocal
from models import CourseModel, ResponseCourse
from db_models import Course

router = APIRouter()

def get_db():
    """
    Provides a database session dependency for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all course
@router.get("/course", tags=["Course"], response_model=List[ResponseCourse])
async def get_course(db: Session = Depends(get_db)):
    """
    Retrieves all courses from the database.
    
    :param db: Database session
    :type db: Session
    :return: List of all courses
    :rtype: List[ResponseCourse]
    """

    cources = db.query(Course).all()
    return cources

# Add Course
@router.post("/course/add", tags=["Course"])
async def add_course(course_form: CourseModel, db: Session = Depends(get_db)):
    """
    Adds a new course to the database.
    
    :param course_form: Course data to be added
    :type course_form: CourseModel
    :param db: Database session
    :type db: Session
    :return: Success message
    :rtype: dict
    """
    new_course = Course(**course_form.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {'message': 'Course Uploaded Succesfully'}

# Update course
@router.put("/course/update/{course_id}", tags=["Course"])
async def update_course(course_id: int, update_course_form: CourseModel,db: Session = Depends(get_db)):
    """
    Updates an existing course in the database.
    
    :param course_id: ID of the course to update
    :type course_id: int
    :param update_course_form: Updated course data
    :type update_course_form: CourseModel
    :param db: Database session
    :type db: Session
    :return: Success message
    :rtype: dict
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    # verify the course exists or not
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The course with id={course_id} doesn't exists"
        )
    
    # Extract update data as a dict
    course_update = update_course_form.model_dump(exclude_unset=True)
    # Apply changes to the model instance
    for key, value in course_update.items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return {"message": "Course Update Success"}

# delete Course
@router.delete("/course/delete/{course_id}", tags=["Course"])
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Deletes a course from the database.
    
    :param course_id: ID of the course to delete
    :type course_id: int
    :param db: Database session
    :type db: Session
    :return: Success message
    :rtype: dict
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course Not found"
        )
    
    db.delete(course)
    db.commit()
    return {"message": "Course removed"}

# Filter courses by grade or catagory
@router.get("/course/{query}", tags=["Course"], response_model=List[ResponseCourse])
async def filter_course(query: str, db: Session = Depends(get_db)):
    """
    Filters courses by category or grade based on the query.
    
    :param query: Category (math, science, ict) or grade (6, 10, 12)
    :type query: str
    :param db: Database session
    :type db: Session
    :return: List of filtered courses
    :rtype: List[ResponseCourse]
    """
    query_lower = query.lower()
    if query_lower in ["math", "science", "ict"]:
        courses = db.query(Course).filter(Course.catagory == query_lower).all()
    elif query in ["6", "10", "12"]:
        courses = db.query(Course).filter(Course.grade == int(query)).all()
    else:
        # If query doesn't match, return empty list or all courses? Assuming empty for now
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invilad Catagory"
        )
    if not courses:
        raise HTTPException(
            status_code=status.HTTP_200_OK, 
            detail="There is Not course till date on this catagory"
            )
    return courses
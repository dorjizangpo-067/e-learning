from pydantic import BaseModel, Field
from typing import Literal

class CourseModel(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    course_url: str = Field(..., min_length=1)
    category: Literal["science", "math", "ict"]
    grade: Literal[6, 8, 10, 12]

    class Config:
        from_attributes = True


class ResponseCourse(BaseModel):
    id: int
    title: str
    description: str
    author: str
    course_url: str
    category: str
    grade: int

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

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


class StudentModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    subscribed: bool
    subscription_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginModel(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

    class Config:
        from_attributes = True
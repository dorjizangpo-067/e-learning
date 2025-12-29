from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime

class CourseModel(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    course_url: str = Field(..., min_length=1)
    category: Literal["science", "math", "ict"]
    grade: Literal[6, 8, 10, 12]

    model_config = ConfigDict(from_attributes=True)


class ResponseCourse(BaseModel):
    id: int
    title: str
    description: str
    author: str
    course_url: str
    category: str
    grade: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    role: Optional[str] = Field(default="student", pattern="^(admin|student)$")

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    subscribed: bool
    subscription_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoginModel(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

    model_config = ConfigDict(from_attributes=True)
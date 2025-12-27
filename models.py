from pydantic import BaseModel, conint
from typing import Literal

class CourseModel(BaseModel):
    title: str
    description: str
    price: float
    author: str
    course_url: str
    catagory: Literal["science", "math", "ict"]
    grade: Literal['6', '8', '10', '12']

class ResponseCourse(BaseModel):
    title: str
    description: str
    price: float
    author: str
    course_url: str
    class Config:
        from_attributes = True
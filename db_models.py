from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    author = Column(String(100), nullable=False)
    course_url = Column(String, nullable=False)
    catagory = Column(String(100))
    grade = Column(Integer)
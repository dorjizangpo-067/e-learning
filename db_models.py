from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    author = Column(String(100), nullable=False)
    course_url = Column(String, nullable=False)
    category = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title='{self.title}', category='{self.category}', grade={self.grade})>"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    subscribed = Column(Boolean, default=False)
    subscription_date = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}', email='{self.email}', subscribed={self.subscribed})>"
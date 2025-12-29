from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), nullable=False, default="student")  # 'admin' or 'student'
    subscribed = Column(Boolean, default=False)
    subscription_date = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}', role='{self.role}', subscribed={self.subscribed})>"
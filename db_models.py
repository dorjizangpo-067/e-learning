from sqlalchemy import Column, Integer, String
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
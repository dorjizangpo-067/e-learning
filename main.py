from fastapi import FastAPI

from course import router
from db_models import Base
from database import engine

app = FastAPI(title="E-Learning For STEM subject BHUTAN ")

# Creating table in database 
Base.metadata.create_all(engine)

# Routes from course.py
app.include_router(router)

@app.get("/", tags=["Home"])
def home():
    return {"message": "Welcome to E-Learning Waktsa Bak"}




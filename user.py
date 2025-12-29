from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from db_models import User
from models import UserModel, UserResponse, LoginModel
from jwt_setup import create_access_token, logout, check_token

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    """
    Provides a database session dependency for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/user/register", tags=["User"], response_model=UserResponse)
async def register_user(user: UserModel, db: Session = Depends(get_db)) -> UserResponse:
    """
    Registers a new user in the database.

    :param user: User registration data
    :param db: Database session
    :return: The registered user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Check if trying to register as admin and admin already exists
    if user.role == "admin":
        admin_exists = db.query(User).filter(User.role == "admin").first()
        if admin_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin user already exists"
            )

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        subscribed=False,
        subscription_date=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/user/login", tags=["User"])
async def login_user(login: LoginModel, db: Session = Depends(get_db)):
    """
    Authenticates a user by checking email and password.

    :param login: Login credentials
    :param db: Database session
    :return: Success message if authenticated
    """
    user = db.query(User).filter(User.email == login.email).first()
    if not user or not pwd_context.verify(login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token with required data
    token_data = {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "subscribed": user.subscribed,
        "subscription_date": user.subscription_date.isoformat() if user.subscription_date else None
    }
    access_token = create_access_token(token_data)
    
    # Create response with cookie
    response = JSONResponse({"message": "Login successful", "access_token": access_token})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.post("/user/logout", tags=["User"])
async def logout_user(request: Request):
    """
    Logs out the user by deleting the access token cookie.
    Requires the user to be logged in.
    """
    # Verify user is logged in
    check_token(request)
    
    # Proceed with logout
    return logout()
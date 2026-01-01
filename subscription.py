from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from database import SessionLocal
from db_models import User
from models import UserModel, UserResponse

router = APIRouter()

# Common price for subscription (in Bhutanese Ngultrum or any currency)
SUBSCRIPTION_PRICE = 100.0
SUBSCRIPTION_DURATION_DAYS = 30


def get_db():
    """
    Provides a database session dependency for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Dependency to get current user and verify they are admin.
    
    :param request: FastAPI Request object
    :param db: Database session
    :return: User data dict if admin
    """
    from jwt_setup import check_token
    token_data = check_token(request)
    user_email = token_data["user"]["email"]
    
    # Fetch current user data from database
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "subscribed": user.subscribed,
        "subscription_date": user.subscription_date.isoformat() if user.subscription_date else None
    }


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Dependency to get current user from JWT.
    
    :param request: FastAPI Request object
    :param db: Database session
    :return: User object
    """
    from jwt_setup import check_token
    token_data = check_token(request)
    user_email = token_data["user"]["email"]
    
    # Fetch current user data from database
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/subscription/purchase", tags=["Subscription"])
async def purchase_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """
    Purchases a subscription for the current user. Sets subscribed to True and records the date.

    :param current_user: Current authenticated user
    :param db: Database session
    :return: Success message with subscription details or already purchased message
    """
    if current_user.subscribed:
        return {"message": "Already purchased"}

    # Set subscription
    current_user.subscribed = True
    current_user.subscription_date = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Subscription purchased successfully",
        "user_id": current_user.id,
        "subscription_date": current_user.subscription_date,
        "expires_on": current_user.subscription_date + timedelta(days=SUBSCRIPTION_DURATION_DAYS),
        "price": SUBSCRIPTION_PRICE
    }


@router.get("/subscription/check/{email}", tags=["Subscription"])
async def check_subscription(
    email: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> dict:
    """
    Checks if a user's subscription is active (within 30 days). Admin only.

    :param email: Email of the user
    :param current_admin: Current admin user
    :param db: Database session
    :return: Subscription status
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.subscribed or not user.subscription_date:
        return {"subscribed": False, "message": "No active subscription"}

    expires_on = user.subscription_date.replace(tzinfo=timezone.utc) + timedelta(days=SUBSCRIPTION_DURATION_DAYS)
    if datetime.now(timezone.utc) > expires_on:
        # Optionally, set subscribed to False if expired
        user.subscribed = False
        db.commit()
        return {"subscribed": False, "message": "Subscription expired"}

    return {
        "subscribed": True,
        "subscription_date": user.subscription_date,
        "expires_on": expires_on,
        "days_left": (expires_on - datetime.now(timezone.utc)).days
    }


@router.get("/users", tags=["Subscription"], response_model=list[UserResponse])
async def get_all_users(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> list[UserResponse]:
    """
    Retrieves all users (for admin purposes). Admin only.

    :param current_admin: Current admin user
    :param db: Database session
    :return: List of all users
    """
    users = db.query(User).all()
    return users
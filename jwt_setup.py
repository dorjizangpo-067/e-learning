import jwt
import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from database import Settings

settings = Settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# CREATE TOKEN
def create_access_token(data: dict) -> str:
    """
    Creates a JWT access token.

    :param data: Data to encode in the token
    :return: Encoded JWT token as a string
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# VERIFY TOKEN
def check_token(request: Request):
    """
    Verifies a JWT access token from cookies or Authorization header.

    :param request: FastAPI Request object
    :return: Dictionary with status and user information
    """
    token = request.cookies.get("access_token")
    if not token:
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer "
        else:
            raise HTTPException(status_code=401, detail="No token found in cookies or Authorization header")

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "status": "Valid token", "user": decoded
            }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# LOGOUT (REMOVE COOKIE)
def logout():
    """Logs out the user by deleting the access token cookie."""
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("access_token")
    return response
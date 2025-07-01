from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx

from database import get_db
from models import User
from schemas import OAuthUserInfo

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

class OAuthService:
    @staticmethod
    async def get_google_user_info(access_token: str) -> OAuthUserInfo:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info from Google")

            data = response.json()
            return OAuthUserInfo(
                email=data["email"],
                name=data["name"],
                picture=data.get("picture"),
                provider="google",
                provider_id=data["id"]
            )

    @staticmethod
    async def get_facebook_user_info(access_token: str) -> OAuthUserInfo:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me?fields=id,name,email,picture&access_token={access_token}"
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info from Facebook")

            data = response.json()
            return OAuthUserInfo(
                email=data["email"],
                name=data["name"],
                picture=data["picture"]["data"]["url"] if "picture" in data else None,
                provider="facebook",
                provider_id=data["id"]
            )

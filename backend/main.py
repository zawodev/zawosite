from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import secrets
import string
from dotenv import load_dotenv

from database import get_db, init_db, database
from models import User as UserModel, UserRole
from schemas import User, UserCreate, Token, OAuthUserInfo, UserProfile
from auth import create_access_token, get_current_user, get_current_admin_user, OAuthService

load_dotenv()

app = FastAPI(title="zawosite api", version="1.0.1")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_unique_username(base_name: str, db: Session) -> str:
    """Generate unique username from base name"""
    # Clean base name
    base = "".join(c.lower() for c in base_name if c.isalnum())
    if not base:
        base = "user"

    # Try original first
    if not db.query(UserModel).filter(UserModel.username == base).first():
        return base

    # Try with numbers
    for i in range(1, 1000):
        username = f"{base}{i}"
        if not db.query(UserModel).filter(UserModel.username == username).first():
            return username

    # Fallback with random string
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{base}_{random_suffix}"

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

    # Create admin user if not exists
    db = next(get_db())
    admin = db.query(UserModel).filter(UserModel.email == "admin@example.com").first()
    if not admin:
        admin_user = UserModel(
            email="admin@example.com",
            full_name="Admin User",
            username="admin",
            provider="system",
            provider_id="admin",
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Server-side OAuth endpoints
@app.get("/auth/google")
async def google_auth_redirect():
    """Redirect to Google OAuth"""
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/google/callback"

    google_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline"
    )

    return RedirectResponse(url=google_url)

@app.get("/auth/google/callback")
async def google_auth_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token
        user_info = await OAuthService.exchange_google_code_for_user_info(code)
        user = authenticate_or_create_user(db, user_info)
        token = create_access_token(data={"sub": str(user.id)})

        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={token}")
    except Exception as e:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/login?error=oauth_error")

@app.get("/auth/facebook")
async def facebook_auth_redirect():
    """Redirect to Facebook OAuth"""
    facebook_app_id = os.getenv("FACEBOOK_APP_ID")
    redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/facebook/callback"

    facebook_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={facebook_app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=email&"
        f"response_type=code"
    )

    return RedirectResponse(url=facebook_url)

@app.get("/auth/facebook/callback")
async def facebook_auth_callback(code: str, db: Session = Depends(get_db)):
    """Handle Facebook OAuth callback"""
    try:
        user_info = await OAuthService.exchange_facebook_code_for_user_info(code)
        user = authenticate_or_create_user(db, user_info)
        token = create_access_token(data={"sub": str(user.id)})

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={token}")
    except Exception as e:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/login?error=oauth_error")

def authenticate_or_create_user(db: Session, user_info: OAuthUserInfo) -> UserModel:
    # Check if user exists
    user = db.query(UserModel).filter(
        UserModel.email == user_info.email,
        UserModel.provider == user_info.provider
    ).first()

    if not user:
        # Generate unique username
        username = generate_unique_username(user_info.name, db)

        # Create new user
        user = UserModel(
            email=user_info.email,
            full_name=user_info.name,
            username=username,
            avatar_url=user_info.picture,
            provider=user_info.provider,
            provider_id=user_info.provider_id,
            role=UserRole.USER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user info
        user.full_name = user_info.name
        user.avatar_url = user_info.picture
        db.commit()
        db.refresh(user)

    return user

# User endpoints
@app.get("/me", response_model=User)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return User.from_orm(current_user)

@app.get("/users", response_model=List[User])
async def get_users(db: Session = Depends(get_db)):
    """Get all users - no auth required for guest access"""
    users = db.query(UserModel).all()
    return [User.from_orm(user) for user in users]

@app.get("/users/{username}", response_model=UserProfile)
async def get_user_profile(username: str, db: Session = Depends(get_db)):
    """Get user profile by username - no auth required"""
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile.from_orm(user)

@app.post("/users/{username}/friend")
async def add_friend(
        username: str,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Add friend"""
    friend = db.query(UserModel).filter(UserModel.username == username).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    if friend.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as friend")

    if friend not in current_user.friends:
        current_user.friends.append(friend)
        db.commit()

    return {"message": "Friend added successfully"}

@app.delete("/users/{username}/friend")
async def remove_friend(
        username: str,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Remove friend"""
    friend = db.query(UserModel).filter(UserModel.username == username).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    if friend in current_user.friends:
        current_user.friends.remove(friend)
        db.commit()

    return {"message": "Friend removed successfully"}

@app.get("/admin/users", response_model=List[User])
async def get_users_admin(
        current_user: UserModel = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    users = db.query(UserModel).all()
    return [User.from_orm(user) for user in users]

@app.get("/")
async def root():
    return {"message": "OAuth App API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

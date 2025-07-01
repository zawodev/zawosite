from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from database import get_db, init_db, database
from models import User as UserModel, UserRole
from schemas import User, UserCreate, Token, OAuthUserInfo
from auth import create_access_token, get_current_user, get_current_admin_user, OAuthService

load_dotenv()

app = FastAPI(title="OAuth App API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            provider="system",
            provider_id="admin",
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Auth endpoints
@app.post("/auth/google", response_model=Token)
async def google_auth(access_token: str, db: Session = Depends(get_db)):
    try:
        user_info = await OAuthService.get_google_user_info(access_token)
        user = authenticate_or_create_user(db, user_info)
        token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=token, token_type="bearer", user=User.from_orm(user))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/facebook", response_model=Token)
async def facebook_auth(access_token: str, db: Session = Depends(get_db)):
    try:
        user_info = await OAuthService.get_facebook_user_info(access_token)
        user = authenticate_or_create_user(db, user_info)
        token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=token, token_type="bearer", user=User.from_orm(user))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def authenticate_or_create_user(db: Session, user_info: OAuthUserInfo) -> UserModel:
    # Check if user exists
    user = db.query(UserModel).filter(
        UserModel.email == user_info.email,
        UserModel.provider == user_info.provider
    ).first()

    if not user:
        # Create new user
        user = UserModel(
            email=user_info.email,
            full_name=user_info.name,
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
async def get_users(
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    users = db.query(UserModel).all()
    return [User.from_orm(user) for user in users]

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
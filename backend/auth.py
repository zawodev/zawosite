import httpx
import os
from urllib.parse import urlencode
from fastapi import HTTPException
from pydantic import BaseModel
from schemas import OAuthUserInfo

class OAuthService:
    @staticmethod
    async def exchange_google_code_for_user_info(code: str) -> OAuthUserInfo:
        """Exchange Google OAuth code for user info"""
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/google/callback"
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")

            token_data = token_response.json()
            access_token = token_data["access_token"]

            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info from Google")

            data = user_response.json()
            return OAuthUserInfo(
                email=data["email"],
                name=data["name"],
                picture=data.get("picture"),
                provider="google",
                provider_id=data["id"]
            )

    @staticmethod
    async def exchange_facebook_code_for_user_info(code: str) -> OAuthUserInfo:
        """Exchange Facebook OAuth code for user info"""
        # Exchange code for access token
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        token_params = {
            "client_id": os.getenv("FACEBOOK_APP_ID"),
            "client_secret": os.getenv("FACEBOOK_APP_SECRET"),
            "code": code,
            "redirect_uri": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/facebook/callback"
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.get(token_url, params=token_params)
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")

            token_data = token_response.json()
            access_token = token_data["access_token"]

            # Get user info
            user_response = await client.get(
                f"https://graph.facebook.com/me?fields=id,name,email,picture&access_token={access_token}"
            )

            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info from Facebook")

            data = user_response.json()
            return OAuthUserInfo(
                email=data["email"],
                name=data["name"],
                picture=data["picture"]["data"]["url"] if "picture" in data else None,
                provider="facebook",
                provider_id=data["id"]
            )

    # Keep existing methods for backward compatibility
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

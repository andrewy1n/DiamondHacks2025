import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
from typing import Optional

load_dotenv()

app = FastAPI(
    title="Auth0 User Info Service",
    description="A service that validates Auth0 tokens and returns user information",
    version="1.0.0"
)

security = HTTPBearer()

# Auth0 Configuration - Replace these with your Auth0 settings
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE") # API Audience/Identifier in Auth0
ALGORITHMS = ["RS256"]

class UserInfo(BaseModel):
    sub: str  # The unique identifier for the user
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    middle_name: Optional[str] = None
    nickname: Optional[str] = None
    preferred_username: Optional[str] = None
    profile: Optional[str] = None
    picture: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    gender: Optional[str] = None
    birthdate: Optional[str] = None
    zoneinfo: Optional[str] = None
    locale: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_verified: Optional[bool] = None
    address: Optional[dict] = None
    updated_at: Optional[str] = None

async def get_jwks():
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        return response.json()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # In a production environment, you would:
    # 1. Verify the token signature using the JWKS from Auth0
    # 2. Check the token claims (iss, aud, exp, etc.)
    # For simplicity, we'll just call Auth0's userinfo endpoint here
    
    userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/me", response_model=UserInfo)
async def get_user_info(user_info: dict = Depends(verify_token)):
    """
    Returns the user information from the validated Auth0 access token.
    Requires a valid Auth0 access token in the Authorization header.
    """
    return user_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
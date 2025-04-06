from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Auth0User(BaseModel):
    sub: str
    name: Optional[str] = None
    email: Optional[str] = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Auth0User:
    try:
        token = credentials.credentials
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        issuer = f"https://{AUTH0_DOMAIN}/"
        
        payload = jwt.decode(
            token,
            key=jwks_url,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=issuer,
            options={"verify_aud": True, "verify_iss": True}
        )
        return Auth0User(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
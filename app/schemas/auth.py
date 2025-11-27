from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """OAuth2 token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data stored in JWT token"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    is_admin: Optional[bool] = None


class LoginRequest(BaseModel):
    """JSON-based login request (alternative to OAuth2 form)"""
    email: EmailStr
    password: str


class OAuth2LoginRequest(BaseModel):
    """OAuth2 compatible login request"""
    username: str  # Can be email or username
    password: str
    grant_type: Optional[str] = None
    scope: str = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

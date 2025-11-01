from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import UserCreate, UserOut
from ..schemas.auth import LoginRequest, Token
from ..services.auth_service import register_user, authenticate_user
from ..core.security import get_password_hash


router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, payload)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login using username (email) and password.
    This is the standard endpoint for OAuth2PasswordBearer.
    """
    # OAuth2 uses 'username' field, but we accept email
    token = authenticate_user(db, form_data.username, form_data.password)
    return token


@router.post("/login/json", response_model=Token)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Alternative JSON-based login endpoint.
    Use this if you prefer sending JSON instead of form data.
    """
    token = authenticate_user(db, payload.email, payload.password)
    return token

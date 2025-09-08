from datetime import timedelta
from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate
from ..schemas.auth import Token
from ..core.security import get_password_hash, verify_password, create_access_token
from ..exceptions import UnauthorizedException, ValidationException


def register_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise ValidationException("Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Token:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid email or password")

    access_token = create_access_token({"sub": user.email, "user_id": user.id}, timedelta(minutes=60))
    return Token(access_token=access_token)

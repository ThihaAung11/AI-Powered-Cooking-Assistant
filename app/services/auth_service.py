from datetime import timedelta
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models import User, Role
from ..schemas.user import UserCreate
from ..schemas.auth import Token
from ..core.security import get_password_hash, verify_password, create_access_token
from ..exceptions import UnauthorizedException, ValidationException


def register_user(db: Session, payload: UserCreate) -> User:
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise ValidationException("Email already registered")
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise ValidationException("Username already taken")
    
    # Get or create default role
    role_id = payload.role_id
    if not role_id:
        default_role = db.query(Role).filter(Role.name == "user").first()
        if not default_role:
            # Create default user role
            default_role = Role(name="user", description="Default user role")
            db.add(default_role)
            db.flush()
        role_id = default_role.id

    user = User(
        username=payload.username,
        name=payload.name,
        email=payload.email,
        password=get_password_hash(payload.password),
        role_id=role_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, user_data: str, password: str) -> Token:
    user = db.query(User).filter(or_(User.email == user_data, User.username == user_data)).first()
    if not user or not verify_password(password, user.password):
        raise UnauthorizedException("Invalid email or password")
    
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")

    access_token = create_access_token(
        {"sub": user.email, "user_id": user.id, "username": user.username},
        timedelta(minutes=60)
    )
    return Token(access_token=access_token)

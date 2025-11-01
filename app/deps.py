from fastapi import Depends
from typing import Optional, Annotated
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.user import User
from app.database import get_db

CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalCurrentUser = Annotated[Optional[User], Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_db)]
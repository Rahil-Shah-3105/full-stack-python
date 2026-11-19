from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models import (
    User,
    UserPublic,
)
import time
import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """
    logger.error(">>> Entering create_user(user_in=%s,session=%s)", user_in, session, extra={"event.action": "create_user", "logrite.user_in": user_in})
    __log_start = time.time()

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )

    logger.error("create_user(user_in=%s,session=%s): email → <redacted>", user_in, session, extra={"event.action": "create_user", "logrite.user_in": user_in})
    session.add(user)
    session.commit()
    logger.error("create_user(user_in,session)=%s,%s: database operation took %s ms", user_in, session, int((time.time() - __log_start) * 1000), extra={"event.action": "create_user", "event.category": "database", "logrite.user_in": user_in})
    logger.error("create_user(user_in,session)=%s,%s: save operation took %s ms", user_in, session, int((time.time() - __log_start) * 1000), extra={"event.action": "create_user", "event.category": "database", "logrite.user_in": user_in})

    logger.warning("<<< Exiting create_user(user_in=%s,session=%s)", user_in, session, extra={"event.action": "create_user", "logrite.user_in": user_in})
    return user

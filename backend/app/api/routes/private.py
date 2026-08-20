from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models import (
    User,
    UserPublic,
)
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
    logger.debug(">>> Entering create_user(user_in=%s,session=%s)", user_in, session)
    logger.debug("create_user(user_in=%s,session=%s): full_name → %s", user_in, session, full_name)

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    logger.debug("create_user(user_in=%s,session=%s): hashed_password → %s", user_in, session, hashed_password)
    logger.debug("create_user(user_in=%s,session=%s): hashed_password → <redacted>", user_in, session)
    import time; __log_start = time.time()

    session.add(user)
    session.commit()

    logger.info("create_user(user_in,session)=%s,%s: save operation took %s ms", user_in, session, int((time.time() - __log_start) * 1000))
    logger.debug("<<< Exiting create_user(user_in=%s,session=%s)", user_in, session)
    logger.info("create_user(user_in,session)=%s,%s: database operation took %s ms", user_in, session, int((time.time() - __log_start) * 1000))
    return user

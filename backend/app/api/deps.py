from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
import logging
logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
    logger.error(">>> Entering get_db()", extra={"event.action": "get_db"})
    with Session(engine) as session:
        yield session
        logger.warning("<<< Exiting get_db()", extra={"event.action": "get_db"})


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    logger.error(">>> Entering get_current_user(session=%s,token=<redacted>)", session, extra={"event.action": "get_current_user"})
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        logger.error("Exception in get_current_user(session=%s,token=<redacted>)", session, exc_info=True, extra={"event.action": "get_current_user", "event.category": "process"})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    logger.error("get_current_user(session=%s,token=<redacted>): user → %s", session, user, extra={"event.action": "get_current_user"})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        logger.error("get_current_user(session=%s,token=<redacted>): detail → %s", session, detail, extra={"event.action": "get_current_user"})
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    logger.warning("<<< Exiting get_current_user(session=%s,token=<redacted>)", session, extra={"event.action": "get_current_user"})
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    logger.error(">>> Entering get_current_active_superuser(current_user=%s)", current_user, extra={"event.action": "get_current_active_superuser", "logrite.current_user": current_user})
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    logger.error("get_current_active_superuser(current_user=%s): status_code → %s", current_user, status_code, extra={"event.action": "get_current_active_superuser", "logrite.current_user": current_user})
    logger.warning("<<< Exiting get_current_active_superuser(current_user=%s)", current_user, extra={"event.action": "get_current_active_superuser", "logrite.current_user": current_user})
    return current_user

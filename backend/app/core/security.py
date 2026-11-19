from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings
import logging
logger = logging.getLogger(__name__)

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    logger.error(">>> Entering create_access_token(subject=%s,expires_delta=%s)", subject, expires_delta, extra={"event.action": "create_access_token", "user.name": str(subject), "logrite.expires_delta": expires_delta})
    expire = datetime.now(UTC) + expires_delta
    logger.error("create_access_token(subject=%s,expires_delta=%s): expire → %s", subject, expires_delta, expire, extra={"event.action": "create_access_token", "user.name": str(subject), "logrite.expires_delta": expires_delta})
    to_encode = {"exp": expire, "sub": str(subject)}
    logger.error("create_access_token(subject=%s,expires_delta=%s): to_encode → %s", subject, expires_delta, to_encode, extra={"event.action": "create_access_token", "user.name": str(subject), "logrite.expires_delta": expires_delta})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    logger.error("create_access_token(subject=%s,expires_delta=%s): encoded_jwt → <redacted>", subject, expires_delta, extra={"event.action": "create_access_token", "user.name": str(subject), "logrite.expires_delta": expires_delta})
    logger.warning("<<< Exiting create_access_token(subject=%s,expires_delta=%s)", subject, expires_delta, extra={"event.action": "create_access_token", "user.name": str(subject), "logrite.expires_delta": expires_delta})
    return encoded_jwt


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    logger.error(">>> Entering verify_password(plain_password=<redacted>,hashed_password=<redacted>)", extra={"event.action": "verify_password"})
    logger.warning("<<< Exiting verify_password(plain_password=<redacted>,hashed_password=<redacted>)", extra={"event.action": "verify_password"})
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    logger.error(">>> Entering get_password_hash(password=<redacted>)", extra={"event.action": "get_password_hash"})
    logger.warning("<<< Exiting get_password_hash(password=<redacted>)", extra={"event.action": "get_password_hash"})
    return password_hash.hash(password)

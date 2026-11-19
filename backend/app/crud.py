import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
import time
import logging
logger = logging.getLogger(__name__)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    logger.error(">>> Entering create_user(session=%s,user_create=%s)", session, user_create, extra={"event.action": "create_user", "logrite.user_create": user_create})
    __log_start = time.time()
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    logger.error("create_user(session,user_create)=%s,%s: save operation took %s ms", session, user_create, int((time.time() - __log_start) * 1000), extra={"event.action": "create_user", "event.category": "database", "logrite.user_create": user_create})
    session.commit()
    logger.error("create_user(session,user_create)=%s,%s: database operation took %s ms", session, user_create, int((time.time() - __log_start) * 1000), extra={"event.action": "create_user", "event.category": "database", "logrite.user_create": user_create})
    session.refresh(db_obj)
    logger.warning("<<< Exiting create_user(session=%s,user_create=%s)", session, user_create, extra={"event.action": "create_user", "logrite.user_create": user_create})
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    logger.error(">>> Entering update_user(session=%s,db_user=%s,user_in=%s)", session, db_user, user_in, extra={"event.action": "update_user", "logrite.db_user": db_user, "logrite.user_in": user_in})
    __log_start = time.time()
    user_data = user_in.model_dump(exclude_unset=True)
    logger.error("update_user(session=%s,db_user=%s,user_in=%s): user_data → %s", session, db_user, user_in, user_data, extra={"event.action": "update_user", "logrite.db_user": db_user, "logrite.user_in": user_in})
    extra_data = {}
    logger.error("update_user(session=%s,db_user=%s,user_in=%s): extra_data → %s", session, db_user, user_in, extra_data, extra={"event.action": "update_user", "logrite.db_user": db_user, "logrite.user_in": user_in})
    if "password" in user_data:
        password = user_data["password"]
        logger.error("update_user(session=%s,db_user=%s,user_in=%s): password → <redacted>", session, db_user, user_in, extra={"event.action": "update_user", "logrite.db_user": db_user, "logrite.user_in": user_in})
        hashed_password = get_password_hash(password)
        logger.error("update_user(session=%s,db_user=%s,user_in=%s): hashed_password → <redacted>", session, db_user, user_in, extra={"event.action": "update_user", "logrite.db_user": db_user, "logrite.user_in": user_in})
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    logger.error("update_user(session,db_user,user_in)=%s,%s,%s: save operation took %s ms", session, db_user, user_in, int((time.time() - __log_start) * 1000), extra={"event.action": "update_user", "event.category": "database", "logrite.db_user": db_user, "logrite.user_in": user_in})
    session.commit()
    logger.error("update_user(session,db_user,user_in)=%s,%s,%s: database operation took %s ms", session, db_user, user_in, int((time.time() - __log_start) * 1000), extra={"event.action": "update_user", "event.category": "database", "logrite.db_user": db_user, "logrite.user_in": user_in})
    session.refresh(db_user)
    logger.warning("<<< Exiting update_user(session=%s,db_user=%s,user_in=%s)", session, db_user, user_in, extra={"event.action": "update_user", "logrite.db_user": db_user, "logrite.user_in": user_in})
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    logger.error(">>> Entering get_user_by_email(session=%s,email=<redacted>)", session, extra={"event.action": "get_user_by_email"})
    statement = select(User).where(User.email == email)
    logger.error("get_user_by_email(session=%s,email=<redacted>): statement → %s", session, statement, extra={"event.action": "get_user_by_email"})
    session_user = session.exec(statement).first()
    logger.error("get_user_by_email(session=%s,email=<redacted>): session_user → %s", session, session_user, extra={"event.action": "get_user_by_email"})
    logger.warning("<<< Exiting get_user_by_email(session=%s,email=<redacted>)", session, extra={"event.action": "get_user_by_email"})
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    logger.error(">>> Entering authenticate(session=%s,email=<redacted>,password=<redacted>)", session, extra={"event.action": "authenticate"})
    db_user = get_user_by_email(session=session, email=email)
    logger.error("authenticate(session=%s,email=<redacted>,password=<redacted>): db_user → %s", session, db_user, extra={"event.action": "authenticate"})
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        __log_start = time.time()
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        logger.error("authenticate(session,email,password)=%s,<redacted>,<redacted>: save operation took %s ms", session, int((time.time() - __log_start) * 1000), extra={"event.action": "authenticate", "event.category": "database"})
        logger.debug("authenticate(session=%s,email=<redacted>,password=<redacted>): db_user.hashed_password → <redacted>", session, extra={"event.action": "authenticate"})
        session.commit()
        logger.error("authenticate(session,email,password)=%s,<redacted>,<redacted>: database operation took %s ms", session, int((time.time() - __log_start) * 1000), extra={"event.action": "authenticate", "event.category": "database"})
        session.refresh(db_user)
    logger.warning("<<< Exiting authenticate(session=%s,email=<redacted>,password=<redacted>)", session, extra={"event.action": "authenticate"})
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    logger.error(">>> Entering create_item(session=%s,item_in=%s,owner_id=%s)", session, item_in, owner_id, extra={"event.action": "create_item", "logrite.item_in": item_in, "logrite.owner_id": owner_id})
    __log_start = time.time()
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    logger.error("create_item(session=%s,item_in=%s,owner_id=%s): db_item → %s", session, item_in, owner_id, db_item, extra={"event.action": "create_item", "logrite.item_in": item_in, "logrite.owner_id": owner_id})
    session.commit()
    logger.error("create_item(session,item_in,owner_id)=%s,%s,%s: save operation took %s ms", session, item_in, owner_id, int((time.time() - __log_start) * 1000), extra={"event.action": "create_item", "event.category": "database", "logrite.item_in": item_in, "logrite.owner_id": owner_id})
    session.refresh(db_item)
    logger.error("create_item(session,item_in,owner_id)=%s,%s,%s: database operation took %s ms", session, item_in, owner_id, int((time.time() - __log_start) * 1000), extra={"event.action": "create_item", "event.category": "database", "logrite.item_in": item_in, "logrite.owner_id": owner_id})
    logger.warning("<<< Exiting create_item(session=%s,item_in=%s,owner_id=%s)", session, item_in, owner_id, extra={"event.action": "create_item", "logrite.item_in": item_in, "logrite.owner_id": owner_id})
    return db_item

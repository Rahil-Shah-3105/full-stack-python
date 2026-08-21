import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
import logging
logger = logging.getLogger(__name__)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    logger.debug(">>> Entering create_user(session=%s,user_create=%s)", session, user_create)
    import time; __log_start = time.time()
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    logger.debug("create_user(session=%s,user_create=%s): db_obj → %s", session, user_create, db_obj)
    session.add(db_obj)
    session.commit()
    logger.info("create_user(session,user_create)=%s,%s: save operation took %s ms", session, user_create, int((time.time() - __log_start) * 1000))
    logger.info("create_user(session,user_create)=%s,%s: database operation took %s ms", session, user_create, int((time.time() - __log_start) * 1000))
    session.refresh(db_obj)
    logger.debug("<<< Exiting create_user(session=%s,user_create=%s)", session, user_create)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    logger.debug(">>> Entering update_user(session=%s,db_user=%s,user_in=%s)", session, db_user, user_in)
    user_data = user_in.model_dump(exclude_unset=True)
    logger.debug("update_user(session=%s,db_user=%s,user_in=%s): user_data → %s", session, db_user, user_in, user_data)
    extra_data = {}
    if "password" in user_data:
        logger.debug("update_user(session=%s,db_user=%s,user_in=%s): extra_data → %s", session, db_user, user_in, extra_data)
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        logger.warning("update_user(session=%s,db_user=%s,user_in=%s): password → %s", session, db_user, user_in, password)
        logger.debug("update_user(session=%s,db_user=%s,user_in=%s): password → <redacted>", session, db_user, user_in)
        logger.debug("update_user(session=%s,db_user=%s,user_in=%s): hashed_password → %s", session, db_user, user_in, hashed_password)
        logger.debug("update_user(session=%s,db_user=%s,user_in=%s): hashed_password → <redacted>", session, db_user, user_in)
        import time; __log_start = time.time()
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    logger.info("update_user(session,db_user,user_in)=%s,%s,%s: database operation took %s ms", session, db_user, user_in, int((time.time() - __log_start) * 1000))
    logger.info("update_user(session,db_user,user_in)=%s,%s,%s: save operation took %s ms", session, db_user, user_in, int((time.time() - __log_start) * 1000))
    logger.debug("<<< Exiting update_user(session=%s,db_user=%s,user_in=%s)", session, db_user, user_in)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    logger.debug(">>> Entering get_user_by_email(session=%s,email=%s)", session, email)
    statement = select(User).where(User.email == email)
    logger.debug("get_user_by_email(session=%s,email=%s): statement → %s", session, email, statement)
    session_user = session.exec(statement).first()
    logger.debug("get_user_by_email(session=%s,email=%s): session_user → %s", session, email, session_user)
    logger.debug("<<< Exiting get_user_by_email(session=%s,email=%s)", session, email)
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    logger.debug(">>> Entering authenticate(session=%s,email=%s,password=<redacted>)", session, email)
    db_user = get_user_by_email(session=session, email=email)
    logger.debug("authenticate(session=%s,email=%s,password=<redacted>): db_user → %s", session, email, db_user)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        logger.debug("authenticate(session=%s,email=%s,password=<redacted>): db_user.hashed_password → %s", session, email, db_user.hashed_password)
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        logger.info("authenticate(session,email,password)=%s,%s,<redacted>: save operation took %s ms", session, email, int((time.time() - __log_start) * 1000))
        session.commit()
        session.refresh(db_user)
    logger.debug("<<< Exiting authenticate(session=%s,email=%s,password=<redacted>)", session, email)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    logger.debug(">>> Entering create_item(session=%s,item_in=%s,owner_id=%s)", session, item_in, owner_id)
    import time; __log_start = time.time()
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    logger.debug("create_item(session=%s,item_in=%s,owner_id=%s): db_item → %s", session, item_in, owner_id, db_item)
    session.commit()
    session.refresh(db_item)
    logger.info("create_item(session,item_in,owner_id)=%s,%s,%s: save operation took %s ms", session, item_in, owner_id, int((time.time() - __log_start) * 1000))
    logger.debug("<<< Exiting create_item(session=%s,item_in=%s,owner_id=%s)", session, item_in, owner_id)
    logger.info("create_item(session,item_in,owner_id)=%s,%s,%s: database operation took %s ms", session, item_in, owner_id, int((time.time() - __log_start) * 1000))
    return db_item

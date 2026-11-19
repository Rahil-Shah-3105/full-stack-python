import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
import time
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    logger.error(">>> Entering read_users(session=%s,skip=%s,limit=%s)", session, skip, limit, extra={"event.action": "read_users", "logrite.skip": skip, "logrite.limit": limit})

    count_statement = select(func.count()).select_from(User)
    logger.error("read_users(session=%s,skip=%s,limit=%s): count_statement → %s", session, skip, limit, count_statement, extra={"event.action": "read_users", "logrite.skip": skip, "logrite.limit": limit})
    count = session.exec(count_statement).one()
    logger.error("read_users(session=%s,skip=%s,limit=%s): count → %s", session, skip, limit, count, extra={"event.action": "read_users", "logrite.skip": skip, "logrite.limit": limit})

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = session.exec(statement).all()
    logger.error("read_users(session=%s,skip=%s,limit=%s): users → %s", session, skip, limit, users, extra={"event.action": "read_users", "logrite.skip": skip, "logrite.limit": limit})

    users_public = [UserPublic.model_validate(user) for user in users]
    logger.error("read_users(session=%s,skip=%s,limit=%s): users_public → %s", session, skip, limit, users_public, extra={"event.action": "read_users", "logrite.skip": skip, "logrite.limit": limit})
    logger.warning("<<< Exiting read_users(session=%s,skip=%s,limit=%s)", session, skip, limit, extra={"event.action": "read_users", "logrite.skip": skip, "logrite.limit": limit})
    return UsersPublic(data=users_public, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    logger.error(">>> Entering create_user(session=%s,user_in=%s)", session, user_in, extra={"event.action": "create_user", "logrite.user_in": user_in})
    user = crud.get_user_by_email(session=session, email=user_in.email)
    logger.error("create_user(session=%s,user_in=%s): user → %s", session, user_in, user, extra={"event.action": "create_user", "logrite.user_in": user_in})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        logger.error("create_user(session=%s,user_in=%s): detail → %s", session, user_in, detail, extra={"event.action": "create_user", "logrite.user_in": user_in})

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        logger.error("create_user(session=%s,user_in=%s): email_data → <redacted>", session, user_in, extra={"event.action": "create_user", "logrite.user_in": user_in})
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    logger.warning("<<< Exiting create_user(session=%s,user_in=%s)", session, user_in, extra={"event.action": "create_user", "logrite.user_in": user_in})
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    logger.error(">>> Entering update_user_me(session=%s,user_in=%s,current_user=%s)", session, user_in, current_user, extra={"event.action": "update_user_me", "logrite.user_in": user_in, "logrite.current_user": current_user})
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        logger.error("update_user_me(session=%s,user_in=%s,current_user=%s): existing_user → %s", session, user_in, current_user, existing_user, extra={"event.action": "update_user_me", "logrite.user_in": user_in, "logrite.current_user": current_user})
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
            logger.error("update_user_me(session=%s,user_in=%s,current_user=%s): status_code → %s", session, user_in, current_user, status_code, extra={"event.action": "update_user_me", "logrite.user_in": user_in, "logrite.current_user": current_user})
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    logger.error("update_user_me(session=%s,user_in=%s,current_user=%s): user_data → %s", session, user_in, current_user, user_data, extra={"event.action": "update_user_me", "logrite.user_in": user_in, "logrite.current_user": current_user})
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    logger.warning("<<< Exiting update_user_me(session=%s,user_in=%s,current_user=%s)", session, user_in, current_user, extra={"event.action": "update_user_me", "logrite.user_in": user_in, "logrite.current_user": current_user})
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    logger.error(">>> Entering update_password_me(session=%s,body=%s,current_user=%s)", session, body, current_user, extra={"event.action": "update_password_me", "logrite.current_user": current_user})
    """
    Update own password.
    """
    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
        logger.error("update_password_me(session=%s,body=%s,current_user=%s): status_code → %s", session, body, current_user, status_code, extra={"event.action": "update_password_me", "logrite.current_user": current_user})
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    logger.error("update_password_me(session=%s,body=%s,current_user=%s): hashed_password → <redacted>", session, body, current_user, extra={"event.action": "update_password_me", "logrite.current_user": current_user})
    logger.debug("update_password_me(session=%s,body=%s,current_user=%s): current_user.hashed_password → <redacted>", session, body, current_user, extra={"event.action": "update_password_me", "logrite.current_user": current_user})
    session.add(current_user)
    session.commit()
    logger.warning("<<< Exiting update_password_me(session=%s,body=%s,current_user=%s)", session, body, current_user, extra={"event.action": "update_password_me", "logrite.current_user": current_user})
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    logger.error(">>> Entering read_user_me(current_user=%s)", current_user, extra={"event.action": "read_user_me", "logrite.current_user": current_user})
    logger.warning("<<< Exiting read_user_me(current_user=%s)", current_user, extra={"event.action": "read_user_me", "logrite.current_user": current_user})
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    logger.error(">>> Entering delete_user_me(session=%s,current_user=%s)", session, current_user, extra={"event.action": "delete_user_me", "logrite.current_user": current_user})
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    logger.warning("<<< Exiting delete_user_me(session=%s,current_user=%s)", session, current_user, extra={"event.action": "delete_user_me", "logrite.current_user": current_user})
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    logger.error(">>> Entering register_user(session=%s,user_in=%s)", session, user_in, extra={"event.action": "register_user", "logrite.user_in": user_in})
    user = crud.get_user_by_email(session=session, email=user_in.email)
    logger.error("register_user(session=%s,user_in=%s): user → %s", session, user_in, user, extra={"event.action": "register_user", "logrite.user_in": user_in})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
        logger.error("register_user(session=%s,user_in=%s): detail → %s", session, user_in, detail, extra={"event.action": "register_user", "logrite.user_in": user_in})
    user_create = UserCreate.model_validate(user_in)
    logger.error("register_user(session=%s,user_in=%s): user_create → %s", session, user_in, user_create, extra={"event.action": "register_user", "logrite.user_in": user_in})
    user = crud.create_user(session=session, user_create=user_create)
    logger.warning("<<< Exiting register_user(session=%s,user_in=%s)", session, user_in, extra={"event.action": "register_user", "logrite.user_in": user_in})
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    logger.error(">>> Entering read_user_by_id(user_id=%s,session=%s,current_user=%s)", user_id, session, current_user, extra={"event.action": "read_user_by_id", "user.name": str(user_id), "logrite.current_user": current_user})
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    logger.error("read_user_by_id(user_id=%s,session=%s,current_user=%s): user → %s", user_id, session, current_user, user, extra={"event.action": "read_user_by_id", "user.name": str(user_id), "logrite.current_user": current_user})
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logger.warning("<<< Exiting read_user_by_id(user_id=%s,session=%s,current_user=%s)", user_id, session, current_user, extra={"event.action": "read_user_by_id", "user.name": str(user_id), "logrite.current_user": current_user})
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    logger.error(">>> Entering update_user(session=%s,user_id=%s,user_in=%s)", session, user_id, user_in, extra={"event.action": "update_user", "user.name": str(user_id), "logrite.user_in": user_in})
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    logger.error("update_user(session=%s,user_id=%s,user_in=%s): db_user → %s", session, user_id, user_in, db_user, extra={"event.action": "update_user", "user.name": str(user_id), "logrite.user_in": user_in})
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
        logger.error("update_user(session=%s,user_id=%s,user_in=%s): status_code → %s", session, user_id, user_in, status_code, extra={"event.action": "update_user", "user.name": str(user_id), "logrite.user_in": user_in})
        logger.error("update_user(session=%s,user_id=%s,user_in=%s): detail → %s", session, user_id, user_in, detail, extra={"event.action": "update_user", "user.name": str(user_id), "logrite.user_in": user_in})
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        logger.error("update_user(session=%s,user_id=%s,user_in=%s): existing_user → %s", session, user_id, user_in, existing_user, extra={"event.action": "update_user", "user.name": str(user_id), "logrite.user_in": user_in})
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    logger.warning("<<< Exiting update_user(session=%s,user_id=%s,user_in=%s)", session, user_id, user_in, extra={"event.action": "update_user", "user.name": str(user_id), "logrite.user_in": user_in})
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    logger.error(">>> Entering delete_user(session=%s,current_user=%s,user_id=%s)", session, current_user, user_id, extra={"event.action": "delete_user", "logrite.current_user": current_user, "user.name": str(user_id)})
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    logger.error("delete_user(session=%s,current_user=%s,user_id=%s): user → %s", session, current_user, user_id, user, extra={"event.action": "delete_user", "logrite.current_user": current_user, "user.name": str(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
        logger.error("delete_user(session=%s,current_user=%s,user_id=%s): status_code → %s", session, current_user, user_id, status_code, extra={"event.action": "delete_user", "logrite.current_user": current_user, "user.name": str(user_id)})
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    logger.error("delete_user(session=%s,current_user=%s,user_id=%s): statement → %s", session, current_user, user_id, statement, extra={"event.action": "delete_user", "logrite.current_user": current_user, "user.name": str(user_id)})
    session.delete(user)
    session.commit()
    logger.warning("<<< Exiting delete_user(session=%s,current_user=%s,user_id=%s)", session, current_user, user_id, extra={"event.action": "delete_user", "logrite.current_user": current_user, "user.name": str(user_id)})
    return Message(message="User deleted successfully")

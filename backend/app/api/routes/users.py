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
    logger.debug(">>> Entering read_users(session=%s,skip=%s,limit=%s)", session, skip, limit)

    count_statement = select(func.count()).select_from(User)
    logger.debug("read_users(session=%s,skip=%s,limit=%s): count_statement → %s", session, skip, limit, count_statement)
    count = session.exec(count_statement).one()
    logger.debug("read_users(session=%s,skip=%s,limit=%s): count → %s", session, skip, limit, count)

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = session.exec(statement).all()
    logger.debug("read_users(session=%s,skip=%s,limit=%s): users → %s", session, skip, limit, users)

    users_public = [UserPublic.model_validate(user) for user in users]
    logger.debug("read_users(session=%s,skip=%s,limit=%s): users_public → %s", session, skip, limit, users_public)
    logger.debug("<<< Exiting read_users(session=%s,skip=%s,limit=%s)", session, skip, limit)
    return UsersPublic(data=users_public, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    logger.debug(">>> Entering create_user(session=%s,user_in=%s)", session, user_in)
    logger.debug("create_user(session=%s,user_in=%s): detail → %s", session, user_in, detail)
    logger.debug("create_user(session=%s,user_in=%s): status_code → %s", session, user_in, status_code)
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        logger.debug("create_user(session=%s,user_in=%s): user → %s", session, user_in, user)
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        logger.debug("create_user(session=%s,user_in=%s): email_to → %s", session, user_in, email_to)
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
        logger.debug("create_user(session=%s,user_in=%s): html_content → %s", session, user_in, html_content)
        logger.debug("create_user(session=%s,user_in=%s): subject → %s", session, user_in, subject)
    logger.debug("<<< Exiting create_user(session=%s,user_in=%s)", session, user_in)
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
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
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    logger.debug(">>> Entering read_user_me(current_user=%s)", current_user)
    logger.debug("<<< Exiting read_user_me(current_user=%s)", current_user)
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    logger.debug(">>> Entering delete_user_me(session=%s,current_user=%s)", session, current_user)
    logger.debug("delete_user_me(session=%s,current_user=%s): status_code → %s", session, current_user, status_code)
    import time; __log_start = time.time()
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    logger.info("delete_user_me(session,current_user)=%s,%s: delete operation took %s ms", session, current_user, int((time.time() - __log_start) * 1000))
    logger.info("delete_user_me(session,current_user)=%s,%s: database operation took %s ms", session, current_user, int((time.time() - __log_start) * 1000))
    session.commit()
    logger.debug("<<< Exiting delete_user_me(session=%s,current_user=%s)", session, current_user)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    logger.debug(">>> Entering register_user(session=%s,user_in=%s)", session, user_in)
    logger.debug("register_user(session=%s,user_in=%s): detail → %s", session, user_in, detail)
    logger.debug("register_user(session=%s,user_in=%s): status_code → %s", session, user_in, status_code)
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        logger.debug("register_user(session=%s,user_in=%s): user → %s", session, user_in, user)
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    logger.debug("register_user(session=%s,user_in=%s): user_create → %s", session, user_in, user_create)
    user = crud.create_user(session=session, user_create=user_create)
    logger.debug("<<< Exiting register_user(session=%s,user_in=%s)", session, user_in)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
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
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")

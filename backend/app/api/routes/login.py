from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.models import Message, NewPassword, Token, UserPublic, UserUpdate
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)
import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    logger.error(">>> Entering test_token(current_user=%s)", current_user, extra={"event.action": "test_token", "logrite.current_user": current_user})
    logger.warning("<<< Exiting test_token(current_user=%s)", current_user, extra={"event.action": "test_token", "logrite.current_user": current_user})
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    logger.error(">>> Entering recover_password(email=<redacted>,session=%s)", session, extra={"event.action": "recover_password"})
    user = crud.get_user_by_email(session=session, email=email)
    logger.error("recover_password(email=<redacted>,session=%s): user → %s", session, user, extra={"event.action": "recover_password"})

    # Always return the same response to prevent email enumeration attacks
    # Only send email if user actually exists
    if user:
        password_reset_token = generate_password_reset_token(email=email)
        logger.error("recover_password(email=<redacted>,session=%s): password_reset_token → <redacted>", session, extra={"event.action": "recover_password"})
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        logger.error("recover_password(email=<redacted>,session=%s): email_data → <redacted>", session, extra={"event.action": "recover_password"})
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
        logger.warning("<<< Exiting recover_password(email=<redacted>,session=%s)", session, extra={"event.action": "recover_password"})
    return Message(
        message="If that email is registered, we sent a password recovery link"
    )


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    logger.error(">>> Entering reset_password(session=%s,body=%s)", session, body, extra={"event.action": "reset_password"})
    email = verify_password_reset_token(token=body.token)
    logger.error("reset_password(session=%s,body=%s): email → <redacted>", session, body, extra={"event.action": "reset_password"})
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    logger.error("reset_password(session=%s,body=%s): user → %s", session, body, user, extra={"event.action": "reset_password"})
    if not user:
        # Don't reveal that the user doesn't exist - use same error as invalid token
        raise HTTPException(status_code=400, detail="Invalid token")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user_in_update = UserUpdate(password=body.new_password)
    logger.error("reset_password(session=%s,body=%s): user_in_update → %s", session, body, user_in_update, extra={"event.action": "reset_password"})
    crud.update_user(
        session=session,
        db_user=user,
        user_in=user_in_update,
    )
    logger.warning("<<< Exiting reset_password(session=%s,body=%s)", session, body, extra={"event.action": "reset_password"})
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    logger.error(">>> Entering recover_password_html_content(email=<redacted>,session=%s)", session, extra={"event.action": "recover_password_html_content"})
    user = crud.get_user_by_email(session=session, email=email)
    logger.error("recover_password_html_content(email=<redacted>,session=%s): user → %s", session, user, extra={"event.action": "recover_password_html_content"})

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
        logger.error("recover_password_html_content(email=<redacted>,session=%s): detail → %s", session, detail, extra={"event.action": "recover_password_html_content"})
    password_reset_token = generate_password_reset_token(email=email)
    logger.error("recover_password_html_content(email=<redacted>,session=%s): password_reset_token → <redacted>", session, extra={"event.action": "recover_password_html_content"})
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    logger.error("recover_password_html_content(email=<redacted>,session=%s): email_data → <redacted>", session, extra={"event.action": "recover_password_html_content"})

    logger.warning("<<< Exiting recover_password_html_content(email=<redacted>,session=%s)", session, extra={"event.action": "recover_password_html_content"})
    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )

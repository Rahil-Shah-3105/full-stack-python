import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import emails
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    logger.error(">>> Entering render_email_template(template_name=%s,context=%s)", template_name, context, extra={"event.action": "render_email_template", "logrite.template_name": template_name})
    template_str = (
        Path(__file__).parent / "email-templates" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    logger.error("render_email_template(template_name=%s,context=%s): html_content → %s", template_name, context, html_content, extra={"event.action": "render_email_template", "logrite.template_name": template_name})
    logger.warning("<<< Exiting render_email_template(template_name=%s,context=%s)", template_name, context, extra={"event.action": "render_email_template", "logrite.template_name": template_name})
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    logger.error(">>> Entering send_email(email_to=<redacted>,subject=%s,html_content=%s)", subject, html_content, extra={"event.action": "send_email", "user.name": str(subject), "logrite.html_content": html_content})
    logger.error("send_email(email_to=<redacted>,subject=%s,html_content=%s): html_content → %s", subject, html_content, html_content, extra={"event.action": "send_email", "user.name": str(subject), "logrite.html_content": html_content})
    assert settings.emails_enabled, "no provided configuration for email variables"
    assert settings.EMAILS_FROM_EMAIL  # For type checker
    message = emails.message.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    logger.error("send_email(email_to=<redacted>,subject=%s,html_content=%s): smtp_options → %s", subject, html_content, smtp_options, extra={"event.action": "send_email", "user.name": str(subject), "logrite.html_content": html_content})
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")
    logger.warning("<<< Exiting send_email(email_to=<redacted>,subject=%s,html_content=%s)", subject, html_content, extra={"event.action": "send_email", "user.name": str(subject), "logrite.html_content": html_content})


def generate_test_email(email_to: str) -> EmailData:
    logger.error(">>> Entering generate_test_email(email_to=<redacted>)", extra={"event.action": "generate_test_email"})
    project_name = settings.PROJECT_NAME
    logger.warning("<<< Exiting generate_test_email(email_to=<redacted>)", extra={"event.action": "generate_test_email"})
    subject = f"{project_name} - Test email"
    logger.error("generate_test_email(email_to=<redacted>): subject → %s", subject, extra={"event.action": "generate_test_email"})
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    logger.error(">>> Entering generate_reset_password_email(email_to=<redacted>,email=<redacted>,token=<redacted>)", extra={"event.action": "generate_reset_password_email"})
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    logger.error("generate_reset_password_email(email_to=<redacted>,email=<redacted>,token=<redacted>): subject → %s", subject, extra={"event.action": "generate_reset_password_email"})
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    logger.error("generate_reset_password_email(email_to=<redacted>,email=<redacted>,token=<redacted>): link → %s", link, extra={"event.action": "generate_reset_password_email"})
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    logger.warning("<<< Exiting generate_reset_password_email(email_to=<redacted>,email=<redacted>,token=<redacted>)", extra={"event.action": "generate_reset_password_email"})
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    logger.error(">>> Entering generate_new_account_email(email_to=<redacted>,username=%s,password=<redacted>)", username, extra={"event.action": "generate_new_account_email", "user.name": str(username)})
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    logger.error("generate_new_account_email(email_to=<redacted>,username=%s,password=<redacted>): subject → %s", username, subject, extra={"event.action": "generate_new_account_email", "user.name": str(username)})
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    logger.warning("<<< Exiting generate_new_account_email(email_to=<redacted>,username=%s,password=<redacted>)", username, extra={"event.action": "generate_new_account_email", "user.name": str(username)})
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    logger.error(">>> Entering generate_password_reset_token(email=<redacted>)", extra={"event.action": "generate_password_reset_token"})
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    logger.error("generate_password_reset_token(email=<redacted>): delta → %s", delta, extra={"event.action": "generate_password_reset_token"})
    now = datetime.now(UTC)
    logger.error("generate_password_reset_token(email=<redacted>): now → %s", now, extra={"event.action": "generate_password_reset_token"})
    expires = now + delta
    exp = expires.timestamp()
    logger.error("generate_password_reset_token(email=<redacted>): exp → %s", exp, extra={"event.action": "generate_password_reset_token"})
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    logger.warning("<<< Exiting generate_password_reset_token(email=<redacted>)", extra={"event.action": "generate_password_reset_token"})
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    logger.error(">>> Entering verify_password_reset_token(token=<redacted>)", extra={"event.action": "verify_password_reset_token"})
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        logger.error("Exception in verify_password_reset_token(token=<redacted>)", exc_info=True, extra={"event.action": "verify_password_reset_token", "event.category": "process"})
        logger.warning("<<< Exiting verify_password_reset_token(token=<redacted>)", extra={"event.action": "verify_password_reset_token"})
        return None

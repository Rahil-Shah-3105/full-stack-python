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
    logger.debug(">>> Entering render_email_template(template_name=%s,context=%s)", template_name, context)
    template_str = (
        Path(__file__).parent / "email-templates" / template_name
    ).read_text()
    logger.debug("render_email_template(template_name=%s,context=%s): template_str → %s", template_name, context, template_str)
    html_content = Template(template_str).render(context)
    logger.debug("render_email_template(template_name=%s,context=%s): html_content → %s", template_name, context, html_content)
    logger.debug("<<< Exiting render_email_template(template_name=%s,context=%s)", template_name, context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    logger.debug("<<< Exiting send_email(email_to=%s,subject=%s,html_content=%s)", email_to, subject, html_content)
    assert settings.emails_enabled, "no provided configuration for email variables"
    assert settings.EMAILS_FROM_EMAIL  # For type checker
    message = emails.message.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
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


def generate_test_email(email_to: str) -> EmailData:
    logger.debug(">>> Entering generate_test_email(email_to=%s)", email_to)
    logger.debug("generate_test_email(email_to=%s): subject → %s", email_to, subject)
    project_name = settings.PROJECT_NAME
    logger.debug("generate_test_email(email_to=%s): project_name → %s", email_to, project_name)
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    logger.debug("generate_test_email(email_to=%s): html_content → %s", email_to, html_content)
    logger.debug("generate_test_email(email_to=%s): template_name → %s", email_to, template_name)
    logger.debug("<<< Exiting generate_test_email(email_to=%s)", email_to)
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
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
    logger.debug("generate_reset_password_email(email_to=%s,email=%s,token=<redacted>): link → %s", email_to, email, link)
    logger.debug("generate_reset_password_email(email_to=%s,email=%s,token=<redacted>): html_content → %s", email_to, email, html_content)
    logger.debug("generate_reset_password_email(email_to=%s,email=%s,token=<redacted>): template_name → %s", email_to, email, template_name)
    logger.debug("<<< Exiting generate_reset_password_email(email_to=%s,email=%s,token=<redacted>)", email_to, email)
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
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
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    logger.debug(">>> Entering generate_password_reset_token(email=%s)", email)
    logger.debug("generate_password_reset_token(email=%s): now → %s", email, now)
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    logger.debug("generate_password_reset_token(email=%s): delta → %s", email, delta)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    logger.debug("generate_password_reset_token(email=%s): expires → %s", email, expires)
    logger.debug("generate_password_reset_token(email=%s): exp → %s", email, exp)
    logger.debug("generate_password_reset_token(email=%s): encoded_jwt → %s", email, encoded_jwt)
    logger.debug("<<< Exiting generate_password_reset_token(email=%s)", email)
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None

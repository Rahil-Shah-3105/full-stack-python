from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    logger.error(">>> Entering test_email(email_to=<redacted>)", extra={"event.action": "test_email"})
    email_data = generate_test_email(email_to=email_to)
    logger.error("test_email(email_to=<redacted>): email_data → <redacted>", extra={"event.action": "test_email"})
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    logger.warning("<<< Exiting test_email(email_to=<redacted>)", extra={"event.action": "test_email"})
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    logger.error(">>> Entering health_check()", extra={"event.action": "health_check"})
    logger.warning("<<< Exiting health_check()", extra={"event.action": "health_check"})
    return True

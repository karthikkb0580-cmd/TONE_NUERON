import logging

import resend

from backend.app.core.config import settings
from backend.app.core.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)


def send_email(
    recipient_email: str,
    subject: str,
    body: str,
) -> None:
    resend.api_key = settings.RESEND_API_KEY

    try:
        response = resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [recipient_email],
            "subject": subject,
            "text": body,
        })

        if not response or not response.get("id"):
            raise EmailDeliveryError()

    except EmailDeliveryError:
        logger.error("Email provider did not accept the request")
        raise

    except Exception as exc:
        logger.error(
            "Email delivery failed: %s",
            type(exc).__name__,
        )
        raise EmailDeliveryError() from exc

    logger.info("Email request accepted by provider")


def send_verification_email(
    recipient_email: str,
    otp: str,
) -> None:
    send_email(
        recipient_email=recipient_email,
        subject="Tone Neuron - Verify Your Email",
        body=(
            "Welcome to Tone Neuron 2.0!\n\n"
            f"Your verification code is: {otp}\n\n"
            f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n\n"
            "Never share this code with anyone."
        ),
    )


def send_password_reset_email(
    recipient_email: str,
    otp: str,
) -> None:
    send_email(
        recipient_email=recipient_email,
        subject="Tone Neuron - Reset Your Password",
        body=(
            "We received a request to reset your password.\n\n"
            f"Your password reset code is: {otp}\n\n"
            f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n\n"
            "If you did not request a password reset, "
            "you can ignore this email.\n\n"
            "Never share this code with anyone."
        ),
    )

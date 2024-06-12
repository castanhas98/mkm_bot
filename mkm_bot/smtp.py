import logging
import smtplib

from email.message import EmailMessage
from typing import Optional

from .config import SmtpConfig

PORT = 465
SMTP_SERVER = "smtp.gmail.com"
SUBJECT_BASE = "[MKM BOT] "
SUCCESS = SUBJECT_BASE + "Success"
FAILURE = SUBJECT_BASE + "Failure"
TO_EMAIL = "franciscocastanheira1998@gmail.com"

logger = logging.getLogger(__name__)


def send_email_report(
    config: SmtpConfig, exception: Optional[Exception]
) -> None:
    msg = _prepare_email(config, exception)

    with smtplib.SMTP_SSL(SMTP_SERVER, PORT) as smtp_server:
        smtp_server.login(config.email, config.password)
        logger.info(
            f"Logged in to SMTP server ({SMTP_SERVER}) as {config.email}"
        )

        smtp_server.send_message(msg)
        logger.info(
            f"Sent email to {TO_EMAIL}: {msg}"
        )


def _prepare_email(
    config: SmtpConfig, exception: Optional[Exception]
) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = config.email
    msg['To'] = TO_EMAIL

    success = exception is None

    subject = SUCCESS if success else FAILURE
    msg['Subject'] = subject

    text: str
    if exception:
        text = repr(exception) + "\n" + \
            getattr(exception, "msg", "No message.")
    else:
        "No exceptions."
    msg.set_content(text)

    return msg

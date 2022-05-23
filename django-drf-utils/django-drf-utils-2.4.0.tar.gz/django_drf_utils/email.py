from typing import Optional, Sequence
from smtplib import SMTPException
import logging

from django.core.mail import EmailMessage

from django_drf_utils.config import Email
from django_drf_utils.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


def sendmail(
    subject: str,
    body: str,
    recipients: Sequence[str],
    email_cfg: Optional[Email],
    **kwargs,
):
    if not recipients:
        return
    try:
        EmailMessage(
            subject=(email_cfg and email_cfg.subject_prefix or "") + subject,
            body=body,
            # mypy doesn't like the simpler `email_cfg and email_cfg.from_address` statement
            from_email=None if email_cfg is None else email_cfg.from_address,
            to=recipients,
            **kwargs,
        ).send(fail_silently=False)
    except SMTPException as e:
        logger.error(
            "Failed to send email notification `{subject}` "
            "SMTP server might not be available or credentials are invalid. "
            "Exception: %s",
            e,
        )
        raise ServiceUnavailable() from e

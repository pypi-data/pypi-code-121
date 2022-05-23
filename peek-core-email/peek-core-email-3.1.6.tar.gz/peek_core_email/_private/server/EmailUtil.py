import logging
import os
import smtplib
import socket
from email.mime.text import MIMEText
from typing import List

from peek_core_email._private.storage import Setting
from peek_core_email._private.storage.Setting import globalSetting

logger = logging.getLogger(__name__)


class SendEmail(object):
    def __init__(self, dbSessionCreator):
        settings = globalSetting(dbSessionCreator)
        self._smtpHost = settings[Setting.EMAIL_SMTP_HOST]
        self._sender = settings[Setting.EMAIL_SENDER]

    def sendBlocking(
        self, message: str, subject: str, recipients: List[str], html=False
    ):
        """
        Send email to one or more addresses.
        """

        if not recipients:
            raise Exception("Receipient is missing")

        msg = MIMEText(message, "html" if html else "plain")
        msg["Subject"] = subject
        msg["From"] = self._sender
        msg["To"] = ", ".join(recipients)
        msg.preamble = subject

        try:
            # Send the message via our own SMTP server.
            s = smtplib.SMTP(self._smtpHost)
            if os.getenv("PEEK_SMTP_NEEDS_LOGIN_AND_TLS"):
                s.starttls()
                s.login(
                    os.getenv("PEEK_SMTP_USER"), os.getenv("PEEK_SMTP_PASS")
                )
            s.send_message(msg)
            s.quit()

        except socket.gaierror as e:
            logger.exception(e)
            raise Exception(
                "Peek failed to send your email, please contact Peek admins."
            )

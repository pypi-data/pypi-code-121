"""SMPT Client."""
import smtplib
from typing import List, Optional

from promail.clients.email_manager import OutBoundManager
from promail.core.embedded_attachments import EmbeddedAttachments


class SmtpClient(OutBoundManager):
    """SMPT Client."""

    def __init__(self, account: str, password: str, host: str, port: int = 587) -> None:
        """Initiates SMPT Client.

        Args:
            account (str): Email Address
            password (str): password
            host (str): url of host.
            port (int): Port to connect on.
        """
        super(SmtpClient, self).__init__(account)
        self._password = password
        self._host = host
        self._port = port

    def login(self, server):
        """Login to server."""
        server.ehlo()
        server.starttls()
        server.login(self._account, self._password)

    def send_email(
        self,
        recipients: str = "",
        cc: str = "",
        bcc: str = "",
        subject: str = "",
        htmltext: str = "",
        plaintext: str = "",
        embedded_attachments: Optional[List[EmbeddedAttachments]] = None,
        attachements: Optional[list] = None,
    ) -> None:
        """Send Email.

        Args:
            recipients: semicolon seperated string of recipients will show in to section
            cc: semicolon seperated string of recipients will  be cc'd on email
            bcc: semicolon seperated string of recipients will be bcc'd on email
            subject: Subject of the email
            htmltext: An HTML string of text
            plaintext: A plain text alternative text
            embedded_attachments: List of EmbeddedAttachments included in email.
            attachements: list of filenames or filelike objects
        """
        msg = self.create_message(
            recipients,
            cc,
            bcc,
            subject,
            htmltext,
            plaintext,
            embedded_attachments,
            attachements,
        )
        with smtplib.SMTP(self._host, self._port) as server:
            self.login(server)
            server.sendmail(self._account, recipients, msg.as_string())
            server.close()

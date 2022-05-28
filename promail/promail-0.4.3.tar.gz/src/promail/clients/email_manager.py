"""Abstract Classes for Inbound and outbound mail."""
import abc
import mimetypes
import os
from email.message import EmailMessage
from typing import List, Optional

from promail.core.embedded_attachments import EmbeddedAttachments


class OutBoundManager(abc.ABC):
    """Outbound Mail class template."""

    def __init__(self, account):
        """Initializes OutBoundManager."""
        self._account = account

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
        """Send an email."""
        pass

    @staticmethod
    def guess_types(path: str) -> tuple:
        """Will attempt to guess ctype, subtype and maintype of file.

        Based on https://docs.python.org/3/library/email.examples.html

        Args:
            path: path to attachment file

        Returns:
            tuple: maintype, subtype of file
        """
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        return maintype, subtype

    def add_attachments(self, msg: EmailMessage, attachments: list) -> None:
        """Add attachment to email."""
        for path in attachments:
            filename = os.path.basename(path)
            maintype, subtype = self.guess_types(path)
            with open(path, "rb") as fp:
                msg.add_attachment(
                    fp.read(), maintype=maintype, subtype=subtype, filename=filename
                )

    def create_message(
        self,
        recipients: str = "",
        cc: str = "",
        bcc: str = "",
        subject: str = "",
        htmltext: str = "",
        plaintext: str = "",
        embedded_attachments: Optional[List[EmbeddedAttachments]] = None,
        attachements: Optional[list] = None,
    ):
        """Create Email Message."""
        if attachements is None:
            attachements = []
        if embedded_attachments is None:
            embedded_attachments = []
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._account
        msg["To"] = recipients
        msg["Cc"] = cc
        msg["Bcc"] = bcc
        msg.set_content(plaintext)
        msg.add_alternative(htmltext, subtype="html")
        for embedded_attachment in embedded_attachments:
            maintype, subtype = self.guess_types(embedded_attachment.filepath)
            msg.get_payload()[1].add_related(
                embedded_attachment.read(),
                maintype,
                subtype,
                cid=embedded_attachment.cid,
            )

        self.add_attachments(msg, attachements)
        return msg


class InBoundManager(abc.ABC):
    """Outbound Mail class template."""

    def retrieve_last_items(self: object, max_items: int) -> list:
        """Get a list of last n items received in inbox.

        Args:
            max_items: The Maximum number of items to return
        """
        pass

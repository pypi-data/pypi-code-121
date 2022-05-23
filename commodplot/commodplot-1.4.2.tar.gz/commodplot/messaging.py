import io
import logging
import traceback
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from os import environ
from pathlib import Path
from smtplib import SMTP, SMTPException
from typing import Union

from commodplot import jinjautils

logger = logging.getLogger(__name__)


class EmailBuilder:
    """Easily compose multipart e-mail messages, set headers and add attachments."""

    def __init__(self):
        self.message = MIMEMultipart()

    def set_sender(self, email: str):
        self.message["From"] = email
        return self

    def set_receiver(self, email: str):
        if isinstance(email, list):
            self.message["To"] = ", ".join(email)
        else:
            self.message["To"] = email
        return self

    def set_bcc(self, email: str):
        self.message["Bcc"] = email
        return self

    def set_subject(self, subject: str):
        self.message["Subject"] = subject
        return self

    def set_body(self, body: str, content_type: str = "html"):
        self.message.attach(MIMEText(body, content_type))
        return self

    def attach_file(
        self, file_name: str, attachment_name: str = None, content_id: str = None
    ):
        file_path = Path(file_name)
        try:
            with file_path.open("rb") as attachment:
                part = MIMEApplication(attachment.read())
        except OSError:
            logger.error(f"Cannot add an e-mail attachment {file_name}")
            raise
        # Add headers describing the attachment.
        # Use either the provided attachment name, or file name.
        content_id = content_id or make_msgid(domain="local")
        content_name = attachment_name or file_path.name
        part.add_header("Content-ID", f"<{content_id}>")
        part.add_header("Content-Disposition", f"attachment; filename= {content_name}")
        # Finally, add attachment to the message.
        self.message.attach(part)
        return self

    def attach_image(self, image: Union[str, bytes], content_id: str = None):
        """Attach image part to the message, optionally set the content-id header."""
        content_id = content_id or make_msgid(domain="energy.local")
        part = MIMEImage(image)
        part.add_header("Content-ID", f"<{content_id}>")
        part.add_header("Content-Disposition", f"inline; filename={content_id}")
        self.message.attach(part)
        return self

    def attached_images(self, images: dict):
        """Attached multiple images to message"""
        for content_id, image in images.items():
            part = MIMEImage(image)
            part.add_header("Content-ID", f"<{content_id}>")
            part.add_header("Content-Disposition", f"inline; filename={content_id}")
            self.message.attach(part)
        return self

    def build(self) -> str:
        """Complete the process and return the entire email message as a text."""
        return self.message.as_string()


def compose_and_send_report(
    subject: str,
    content: str,
    images: dict = None,
    sender_email: str = None,
    receiver_email: str = None,
) -> None:
    """
    Compose an e-mail message containing the report and send.

    Configuration:
    * ENV: SENDER_EMAIL - e mail address of the sender
    * ENV: RECEIVER_EMAIL - email address for the recipients
    * ENV: SMTP_HOST - hostname of the SMTP server
    * ENV: SMTP_PORT - port of the SMTP server (default: 25)
    * ENV: SMTP_TIMEOUT - timeout for SMTP operations (default: 60 seconds)
    """

    if not sender_email:
        sender_email = environ.get("SENDER_EMAIL")
    if not receiver_email:
        receiver_email = environ.get("RECEIVER_EMAIL")
    smtp_host = environ.get("SMTP_HOST")
    smtp_port = int(environ.get("SMTP_PORT", "25"))
    smtp_timeout = int(environ.get("SMTP_TIMEOUT", "60"))
    message = (
        EmailBuilder()
        .set_sender(sender_email)
        .set_receiver(receiver_email)
        .set_subject(subject)
        .set_body(content)
    )
    if images:
        message.attached_images(images=images)

    message = message.build()
    logger.info("Sending report e-mail to %s", receiver_email)
    try:
        with SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as client:
            # client.set_debuglevel(1)
            client.connect(smtp_host, smtp_port)
            client.starttls()
            client.sendmail(sender_email, receiver_email, message)
            client.close()
        logger.info("Report sent successfully")
    except SMTPException as ex:
        logger.exception("Failed to send a report")
        errors = io.StringIO()
        logging.error(traceback.print_exc(file=errors))
        contents = str(errors.getvalue())
        logging.error(contents)
        errors.close()


def compose_and_send_jinja_report(
    subject: str,
    data: dict,
    template: str,
    package_loader_name: str = None,
    sender_email: str = None,
    receiver_email: str = None,
    template_globals=None,
):
    message = jinjautils.render_html(
        data=data,
        template=template,
        package_loader_name=package_loader_name,
        plotly_image_conv_func=jinjautils.convert_dict_plotly_fig_png,
        template_globals=template_globals,
    )
    compose_and_send_report(
        subject=subject,
        content=message,
        sender_email=sender_email,
        receiver_email=receiver_email,
    )

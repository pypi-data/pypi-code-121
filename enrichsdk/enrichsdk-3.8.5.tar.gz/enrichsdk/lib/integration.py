import os
import sys
import smtplib
import mimetypes
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage


def attach_files(msg, attachments=[]):

    # https://docs.python.org/3.4/library/email-examples.html
    for path in attachments:

        if (not isinstance(path, str)) or (not os.path.isfile(path)):
            continue

        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        if maintype == "text":
            with open(path) as fp:
                attach = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == "image":
            with open(path, "rb") as fp:
                attach = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == "audio":
            with open(path, "rb") as fp:
                attach = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            with open(path, "rb") as fp:
                attach = MIMEBase(maintype, subtype)
                attach.set_payload(fp.read())
            encoders.encode_base64(attach)

        filename = os.path.basename(path)
        attach.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attach)


def send_html_email(content, sender, receivers, subject, attachments=[]):
    """
    Send HTML email to target audience
    """
    msg = MIMEMultipart()
    msg.attach(MIMEText(content, "html"))

    msg["From"] = sender
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = subject

    # Add payload
    if isinstance(attachments, list) and len(attachments) > 0:
        attach_files(msg, attachments)

    server = os.environ["EMAIL_HOST"]
    username = os.environ["EMAIL_HOST_USER"]
    password = os.environ["EMAIL_HOST_PASSWORD"]
    port = os.environ.get("EMAIL_PORT", "587")
    timeout = os.environ.get("EMAIL_TIMEOUT", "30")

    # Collect the body
    text = msg.as_string()

    smtp = smtplib.SMTP(server, port=int(port), timeout=int(timeout))
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender, receivers, text)

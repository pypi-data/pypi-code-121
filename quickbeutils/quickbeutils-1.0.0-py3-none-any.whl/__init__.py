import os
from quickbelog import Log
import quickbeutils.gmail as gmail
import quickbeutils.aws_ses as aws_ses
import quickbeutils.slack as slack
from email.utils import formataddr
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SEND_EMAIL_VIA_GMAIL = 'GMAIL'
SEND_EMAIL_VIA_SMTP = 'SMTP'
SEND_EMAIL_VIA_AWS_SES = 'AWS_SES'


def send_email(
        sender: str, recipient: str,
        subject: str = None, sender_name: str = None,
        body_text: str = '',
        body_html: str = None,
        send_via: str = SEND_EMAIL_VIA_SMTP) -> bool:
    """

    :param body_html:
    :param body_text:
    :param sender: "From" address
    :param recipient: "To" address.
    :param subject: The subject line of the email.
    :param sender_name: Sender name is optional.
    :param send_via: One of the following: SMTP, AWS_SES, GMAIL
    :return:
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr((sender_name, sender))
    msg['To'] = recipient

    if body_html is None:
        txt = body_text.replace('\n', '<br>')
        body_html = f"<html><head><title>{subject}</title></head><body>{txt}</body></html>"

    # Record the MIME types of both parts - text/plain and text/html
    # According to RFC 2046, the last part of a multipart message, in this case the HTML message is preferred.
    msg.attach(MIMEText(body_text, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))

    send_via = send_via.upper().strip()

    try:
        if send_via == SEND_EMAIL_VIA_AWS_SES:
            aws_ses.send(sender=sender, recipient=recipient, msg=msg)
        elif send_via == SEND_EMAIL_VIA_GMAIL:
            gmail.send(sender=sender, recipient=recipient, msg=msg)
        else:
            raise ValueError(f'Sending method: {send_via} is not supported.')
        return True

    except SMTPException as e:
        Log.exception(f'Failed sending email from {sender} to {recipient} ({e.__class__.__name__} {e})')
        return False


def send_slack_message(recipient_id: str, text: str):
    slack.send_message(recipient_id=recipient_id, text=text)


def send_slack_attachment(recipient_id: str, text: str, file_path: str, file_name: str = None):
    slack.upload_file(recipient_id=recipient_id, comment=text, file_path=file_path, file_name=file_name)


def get_env_var_as_int(key: str, default: int = 0) -> int:
    value = os.getenv(key)
    try:
        default = int(default)
        value = int(float(value))
    except (TypeError, ValueError):
        value = default
    return value


def get_env_var_as_list(key: str, default: list = [], delimiter: str = ' ') -> list:
    value = os.getenv(key, '')
    try:
        tokens = [token.strip() for token in value.strip().split(delimiter)]
    except (TypeError, ValueError):
        value = default
    return tokens

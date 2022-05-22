from os import getenv
from smtplib import SMTP_SSL
from quickbeutils.helpers import verify_config
from email.mime.multipart import MIMEMultipart

GMAIL_SMTP_HOST = 'smtp.gmail.com'
GMAIL_SMTP_PORT = 465
GMAIL_SMTP_USER_KEY = 'GMAIL_SMTP_USER'
GMAIL_SMTP_PASSWORD_KEY = 'GMAIL_SMTP_PASSWORD'


def send(sender: str, recipient: str, msg: MIMEMultipart):
    verify_config(
        conf={
            'GMAIL_SMTP_USER': getenv(GMAIL_SMTP_USER_KEY),
            'GMAIL_SMTP_PASSWORD': getenv(GMAIL_SMTP_PASSWORD_KEY),
        }
    )
    with SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user=getenv(GMAIL_SMTP_USER_KEY), password=getenv(GMAIL_SMTP_PASSWORD_KEY))
        server.sendmail(sender, recipient, msg.as_string())
        server.close()

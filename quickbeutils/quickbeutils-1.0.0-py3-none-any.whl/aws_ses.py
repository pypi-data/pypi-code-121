from os import getenv
from smtplib import SMTP_SSL
from quickbeutils.helpers import verify_config
from email.mime.multipart import MIMEMultipart

AWS_SES_USER_NAME_KEY = 'AWS_SES_USER_NAME'
AWS_SES_PASSWORD_KEY = 'AWS_SES_PASSWORD'
AWS_SES_HOST_KEY = 'AWS_SES_HOST'
AWS_SES_PORT_KEY = 'AWS_SES_PORT'


def send(sender: str, recipient: str, msg: MIMEMultipart):
    conf = {
        'AWS_SES_USER_NAME': getenv(AWS_SES_USER_NAME_KEY),
        'AWS_SES_PASSWORD': getenv(AWS_SES_PASSWORD_KEY),
        'AWS_SES_HOST': getenv(AWS_SES_HOST_KEY)
    }
    try:
        conf[AWS_SES_PORT_KEY] = int(getenv(AWS_SES_PORT_KEY))
    except (ValueError, TypeError):
        conf[AWS_SES_PORT_KEY] = 465

    verify_config(
        conf=conf
    )

    with SMTP_SSL(conf.get(AWS_SES_HOST_KEY), conf.get(AWS_SES_PORT_KEY)) as server:
        server.login(conf.get(AWS_SES_USER_NAME_KEY), conf.get(AWS_SES_PASSWORD_KEY))
        server.sendmail(sender, recipient, msg.as_string())
        server.close()

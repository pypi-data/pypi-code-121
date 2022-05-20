# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Manage email communications including authentication, preparing and sending messages."""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from learner.configuration.configuration import Configuration


class BaseEmailManager:
    """The parent class for email manager subclasses."""
    def __init__(self, conf=None, message=None, data=None):
        self._conf = conf
        self._data = data
        self._message = message

    @property
    def conf(self):
        return self._conf

    @property
    def data(self):
        return self._data

    @property
    def message(self):
        return self._message

    @staticmethod
    def send_email(smtp, msg, username, email_list):
        """Use an authenticated smtp object and a message to send emails.

        :param smtp: an smtp object
        :param msg: the message object to be sent
        :param username: the email username
        :param email_list: the list of emails to send to
        :return: None
        """
        logging.info("Sending emails...")
        smtp.sendmail(username, email_list, msg.as_string())
        smtp.quit()
        logging.info("Emails were sent successfully...")

    def authenticate(self, username, password):
        """Authenticate to the mail server

        :param username: the email username
        :param password: the email password
        :return: an authenticated smtp object
        """
        logging.info("Authenticating to the mail server...")
        smtp = smtplib.SMTP(self.conf.communication.admin_email_host, self.conf.communication.admin_email_port)
        smtp.starttls()
        smtp.login(username, password)
        logging.info("Successfully authenticated to the mail server...")
        return smtp

    @staticmethod
    def prepare_email_content(body, attachment_paths=None):
        """Prepare the email content with body in text. append attachment if provided.

        :param body: the text to use for the body of the email
        :param attachment_paths: list of paths to the attachment file
        :return: an email object
        :rtype: MIMEMultipart
        """
        email = MIMEMultipart()
        text = MIMEText(body, "html")
        email.attach(text)

        if attachment_paths is not None:
            for attachment_path in attachment_paths:
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(open(attachment_path, "rb").read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= {path}".format(path=os.path.split(attachment_path)[-1]))
                email.attach(p)

        return email


class AdminEmailManager(BaseEmailManager):
    """Email managing system for administrative purposes."""
    def __init__(self, conf: Configuration, message=None, data=None):
        super(AdminEmailManager, self).__init__(conf, message=message, data=data)
        self.smtp = None

    def handle_communications(self):
        """Call appropriate methods to make decisions and prepare messages for different communication methods.

        :return: None
        """
        self.smtp = self.authenticate(self._conf.communication.admin_email_ausername, self._conf.communication.admin_email_password)
        msg = getattr(self, "prepare_admin_message")()
        self.send_email(self.smtp, msg, self._conf.communication.admin_email_ausername, self._conf.communication.admin_email_address)

    def prepare_admin_message(self):
        """Prepare the admin email including body, subject, etc.

        :return: an email object
        """
        logging.info("Preparing admin email message...")
        body = self.message

        email = self.prepare_email_content(body)
        email['Subject'] = "[LEARNER ALERT]: " + body
        email['From'] = self._conf.communication.admin_email_ausername
        email['To'] = ", ".join(self._conf.communication.admin_email_address)

        logging.info("Successfully prepared the email message...")
        return email

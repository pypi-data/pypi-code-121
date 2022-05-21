# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import aiosmtplib

from email.message import EmailMessage

from .base import Utils


class EmailBody:

    def __init__(self, sender, recipients, message):

        self._sender = sender
        self._recipients = recipients
        self._message = message

    @property
    def sender(self):
        return self._sender

    @property
    def recipients(self):
        return self._recipients

    @property
    def message(self):
        return self._message

    @staticmethod
    def create_message(sender, recipients, subject, content, content_type=r'text/html'):

        message = EmailMessage()

        if sender is not None:
            message[r'From'] = sender

        if recipients is not None:
            message[r'To'] = recipients

        message[r'Subject'] = subject
        message.set_content(content)
        message.set_type(content_type)

        return message


class SMTPClient:

    def __init__(self, username, password, hostname, port, retry_count=5, **kwargs):

        self._username = username
        self._password = password

        self._hostname = hostname
        self._port = port

        self._retry_count = retry_count

        self._smtp_settings = kwargs

    def format_address(self, nickname, mailbox):

        return f'{nickname}<{mailbox}>'

    def format_addresses(self, items):

        return r';'.join(self.format_address(*item) for item in items)

    # 发送多封邮件
    async def send_messages(self, email_body_list):

        resp = None

        try:

            async with aiosmtplib.SMTP(hostname=self._hostname, port=self._port, **self._smtp_settings) as client:

                await client.login(self._username, self._password)

                for email_body in email_body_list:
                    resp = await client.send_message(email_body.message, email_body.sender, email_body.recipients)
                    Utils.log.info(f'{email_body.recipients} => {resp}')

        except aiosmtplib.SMTPException as err:

            Utils.log.error(err)

        except Exception as err:

            raise err

        return resp

    # 发送单封邮件
    async def send_message(self, sender, recipients, message):

        return await self.send_messages(
            [EmailBody(sender, recipients, message)]
        )

    # 简单的发送
    async def send(self, sender, recipients, subject, content):

        return await self.send_message(
            sender, recipients,
            EmailBody.create_message(sender, recipients, subject, content)
        )

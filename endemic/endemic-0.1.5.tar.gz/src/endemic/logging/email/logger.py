import logging
import logging.handlers
from typing import Tuple, Union, List, Set
from abc import ABC

from logging.handlers import SMTPHandler


from ..interface import LoggerInterface


class SSLSMTPHandler(SMTPHandler):

    def __init__(self,
                 mailhost: Union[str, Tuple[str, int]],
                 fromaddr: str,
                 toaddrs: List[str],
                 subject: str,
                 credentials: Tuple[str, str],
                 secure,
                 start_ssl: bool = False
                 ):

        super().__init__(mailhost, fromaddr, toaddrs, subject, credentials,secure)
        self.__start_ssl = start_ssl

    def emit(self, record):
        """
        Overwrite the logging.handlers.SMTPHandler.emit function with SMTP_SSL.
        Emit a record.
        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            from email.message import EmailMessage
            import email.utils

            smtp = smtplib.SMTP_SSL(
                self.mailhost,
                self.mailport if self.mailport else smtplib.SMTP_PORT)

            smtp.set_debuglevel(1)

            msg = EmailMessage()
            msg['From'] = self.fromaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.getSubject(record)
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))

            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    if self.__start_ssl:
                        smtp.starttls(*self.secure)
                        smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.send_message(msg)
            smtp.quit()
        except Exception:
            self.handleError(record)


class LoggerSMTP(LoggerInterface, ABC):

    def __init__(
            self,
            smtp_host: str,
            smtp_port: int,
            smtp_login: str,
            smtp_pass: str,
            email_from: str,
            emails_to: list,
            level: str = LoggerInterface.DEBUG,
            subject: str = 'Error',
            smtp_start_ssl: bool = False
    ):
        self.__log = logging
        self.__logging_level = level

        self.__smtp = [smtp_host, smtp_port, smtp_login, smtp_pass, smtp_start_ssl]

        self.__email_from = email_from
        self.__email_to = emails_to

        self.__subject = subject

        self.__settings()

    def __repr__(self):
        return self.__log

    def __settings(self):
        print('Setting')
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=self.__logging_level
        )

        self.__log = logging.getLogger(__name__)

        smtp_handler = SSLSMTPHandler(
            mailhost=(self.__smtp[0], int(self.__smtp[1])),
            fromaddr=self.__email_from,
            toaddrs=self.__email_to,
            subject=self.__subject,
            credentials=(self.__smtp[2], self.__smtp[3]),
            secure=())

        self.__log.addHandler(smtp_handler)

    def start_ssl(self) -> bool:
        print('RRRR')
        return bool(self.__smtp[4])

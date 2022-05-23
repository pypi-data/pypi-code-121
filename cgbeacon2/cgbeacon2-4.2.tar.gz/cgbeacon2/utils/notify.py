# -*- coding: utf-8 -*-
import logging
from logging.handlers import SMTPHandler

LOG = logging.getLogger(__name__)


class TlsSMTPHandler(SMTPHandler):
    """Class for handling error logging system"""

    def emit(self, record) -> None:
        """Emit a record.
        Format the record and send it to the specified admin addressees.
        """
        try:
            import smtplib

            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                ",".join(self.toaddrs),
                self.getSubject(record),
                formatdate(),
                msg,
            )
            if self.username:
                smtp.ehlo()  # For 'tls', add this line
                smtp.starttls()  # For 'tls', add this line
                smtp.ehlo()  # For 'tls', add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()

        except Exception as ex:
            LOG.warning(ex)

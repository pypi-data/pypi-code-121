# -*- coding:utf-8 -*-

import logging
import smtplib
import sys

from com.dvsnier.email.message.mtp.smtp import Smtp


class SmtpSSL(Smtp, object):
    ''' the SMTP ssl class that is use for send email '''
    def __init__(self, host, port):
        super(SmtpSSL, self).__init__()
        if sys.version_info.major >= 3 and sys.version_info.minor >= 7:
            self._smtpObj = smtplib.SMTP_SSL(host, port)
            logging.warn(
                'the current Python version ({0}) is greater than or equal to 3.7, and the constructor must set host and port, which can be set by.'
                .format(sys.version))
        else:
            self._smtpObj = smtplib.SMTP_SSL()

    def connect(self, host, port):
        super(SmtpSSL, self).connect(host, port)

    def login(self, user, password):
        super(SmtpSSL, self).login(user, password)

    def sendmail(self, from_addr, to_addrs, msg):
        super(SmtpSSL, self).sendmail(from_addr, to_addrs, msg)

    def quit(self):
        super(SmtpSSL, self).quit()

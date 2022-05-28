# -*- coding:utf-8 -*-

import logging
import smtplib

from com.dvsnier.email.lifecycle.imtpcycle import IMTPCycle
from com.dvsnier.email.message.mtp.smtpbase import SmtpBase


class Smtp(SmtpBase, IMTPCycle, object):
    ''' the SMTP class that is use for send email '''
    def __init__(self):
        super(Smtp, self).__init__()
        self._smtpObj = smtplib.SMTP()

    def connect(self, host, port):
        super(Smtp, self).connect(host, port)
        self._smtpObj.connect(host, port)

    def login(self, user, password):
        super(Smtp, self).login(user, password)
        try:
            self._smtpObj.login(user, password)
        except smtplib.SMTPHeloError or smtplib.SMTPAuthenticationError or smtplib.SMTPException as e:
            logging.exception(e)
            print(e)

    def sendmail(self, from_addr, to_addrs, msg):
        super(Smtp, self).sendmail(from_addr, to_addrs, msg)
        try:
            self._smtpObj.sendmail(from_addr, to_addrs, msg)
        except smtplib.SMTPRecipientsRefused or smtplib.SMTPHeloError or smtplib.SMTPSenderRefused or smtplib.SMTPDataError as e:
            logging.exception(e)
            print(e)

    def quit(self):
        super(Smtp, self).quit()
        self._smtpObj.quit()

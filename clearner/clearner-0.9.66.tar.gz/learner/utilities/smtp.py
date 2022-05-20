# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

# monkey-patch smtplib so we don't send actual emails
smtp=None
inbox=[]


class Message(object):
    def __init__(self, from_address, to_address, fullmessage):
        self.from_address = from_address
        self.to_address = to_address
        self.fullmessage = fullmessage


class DummySMTP(object):
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.username = None
        self.password = None
        self.has_quit = False
        global smtp
        smtp = self

    def login(self, username, password):
        self.username = username
        self.password = password

    def starttls(self):
        return None

    def sendmail(self, from_address, to_address, fullmessage):
        global inbox
        inbox.append(Message(from_address, to_address, fullmessage))
        return []

    def quit(self):
        self.has_quit = True


# this is the actual monkey patch (simply replacing one class with another)
import smtplib
smtplib.SMTP = DummySMTP

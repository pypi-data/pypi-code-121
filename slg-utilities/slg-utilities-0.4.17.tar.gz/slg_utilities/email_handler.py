
import email
import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .helpers import *

ADMINS = []
USERS = []


class EmailHandler:
    '''
    Sends emails, with an easier to use interface

    send an isolated email with the class method EmailHandler.send_one(*args) [NOT IMPLEMENTED]


HOW TO
    Initialize like so:

            email_handler = EmailHandler(server (ex: 'smtp.gmail.com'),
                                            default_from (what the default sending email is),
                                            password (optional if server == 'localhost' else required),
                                            port (optional; default == 465),
                                            admins (optional; if you want to specify common admins to send mail to),
                                            users (optional; if you want to specify common users to send mail to)

HOW TO
    Send email, after initialized, like such:

            email_handler.send_mail('my subject', 'my body', img_attachments=images)
    '''

    def __init__(
            self, server, default_from, password=None, port=None,
            admins=ADMINS, users=USERS):
        self.port = port or 465
        self.password = password if server != 'localhost' else None
        self.default_from = default_from
        self.server_name = server
        self.admins = admins
        self.users = users

    @classmethod
    def init_from_test_settings(cls):
        '''
Instantiates this object ready to send mail to test server

        Run this command in a separate terminal to initialize testing server:
                $ python -m smtpd -n -c DebuggingServer localhost:1025
        '''
        return cls('localhost', port=1025, default_from='testing@example.com')

    @classmethod
    def init_default_settings(cls):

        return cls('smtp.gmail.com', '<your gmail email here>',
                   '<token or password for email here>', 465)

    @classmethod
    def send_one():
        '''
        needs further implementation in a 'best way undetermined' kind of way
        '''

        server = input('What is the server you are sending from? ')
        from_username = input(
            'What user email are you sending from? (ie: bob@gmail.com) ')
        from_password = input(f"Password for {from_username}? ")

    def initialize_server(self):
        '''
        Opens connection to the server as defined by self.server_name
        '''
        if self.server_name == 'localhost':
            self.server = smtplib.SMTP(self.server_name, self.port)
        else:
            self.server = smtplib.SMTP_SSL(self.server_name, self.port)

    def send_mail(self, subject, body, to=None, from_=None,
                  img_attachments=[], img_types='email format', format="text"):
        '''
        sends emails to list of users defined by <to> user_form

        to: list (defaults to self.admins)
                list of users to send email to

        img_attachments: list of images
                expects email ready format ( see ImageHandler.get_email_ready_format() ); two tuple (image_filename, image_bytestring)

        img_types: str
                sets type of element in img_attachments; default == 'email format'
                also supports 'bytestring' if you are passing a list of bytestrings as img_attachments; names will be 'image1.png', 'image2.png', etc.

        #TODO add support for other file attachment types
        #TODO? add support for other image types
        '''
        if to == None:
            to = self.admins
        if type(to) == str:
            to = [to]

        if from_ == None:
            from_ = self.default_from

        self.initialize_server()

        if self.server._host != 'localhost':
            from_ = self.login_to_server(from_)

        msg = MIMEMultipart()
        msg["From"] = from_
        msg["To"] = ', '.join(to)
        msg["Subject"] = subject

        if format == "text":
            msg.attach(MIMEText(body))
        elif format == "html":
            msg.attach(MIMEText(body, 'html'))

        if img_attachments:
            msg = self.attach_images(msg, img_attachments, img_types)

        self.server.sendmail(from_, to, msg.as_string())
        del msg

        self.close_conn()

    def login_to_server(self, from_):
        '''
        handle setting password (if necessary) and logging in with validation of success or authentication error
        '''
        password = self.set_password()
        while True:
            try:
                self.server.login(from_, password)
                break
            except smtplib.SMTPAuthenticationError:
                option = input(
                    'There was an error with authentication. Please press 1 to edit username or 2 to edit password: ')
                if option == '1':
                    from_ = input('Username: ')
                elif option == '2':
                    password = input('Password: ')

        return from_

    def set_password(self):
        '''
        sets password and returns it
        '''
        if self.password:
            password = self.password
        else:
            password = input(
                "Please input the password associated with the sending email: ")

        return password

    def attach_images(self, msg, img_attachments, img_types='email format'):
        '''
        attaches images based on the specific format held by <img_attachments> specified by <img_types>
        '''
        if img_types == 'email format':
            for img in img_attachments:
                image = MIMEImage(img[1], name=img[0])
                msg.attach(image)
        elif img_types == 'bytestring':
            for idx, img in enumerate(img_attachments):
                image = MIMEImage(img, name=f"image{idx}")
                msg.attach(image)

        return msg

    def close_conn(self):
        self.server.quit()

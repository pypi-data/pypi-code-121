# -*- coding:utf-8 -*-

import logging

from com.dvsnier.email.config.config import Config
from com.dvsnier.email.message.builder.mimetextbuilder import MIMETextBuilder
from com.dvsnier.email.message.mtp.smtp import Smtp
from com.dvsnier.email.message.mtp.smtpbase import SmtpBase
from com.dvsnier.email.message.mtp.smtpssl import SmtpSSL
from typing import Optional


class Email(object):
    '''the email class'''

    # the config object
    _config = None  # type: Optional[Config]
    # the Smtp object
    _smtp = None  # type: Optional[SmtpBase]

    def __init__(self):
        '''
            the type comment reference:
                1. https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code

            type: () -> None
        '''
        super(Email, self).__init__()
        self._config = Config()

    def get_config(self):  # type: () -> Config
        ''' the get config information '''
        return self._config

    def update_config(self, config):
        ''' the update config information '''
        if config:
            self._config.update_config(config)
        return self

    def config_file(self, config_file):
        ''' the read xxx.cfg '''
        # logging.debug('the current config file is {}'.format(config_file))
        self.update_config(Config().generate_config(config_file))
        return self

    def get_config_info(self):
        ''' the get config information that dict typing '''
        return self.get_config().get_config()

    def init(self, mode=False):
        '''
            the initlizated email environment
            mode: true that is ssl mode, otherwise no
        '''
        logging.debug('the mail initialization started...')
        if mode:
            self._smtp = SmtpSSL(self.get_config().get_mail_host(), self.get_config().get_mail_port())
        else:
            self._smtp = Smtp()
        self._smtp.connect(self.get_config().get_mail_host(), self.get_config().get_mail_port())
        logging.info('the current connect host that is {0} and port that is {1}.'.format(
            self.get_config().get_mail_host(),
            self.get_config().get_mail_port()))
        self._smtp.login(self.get_config().get_mail_user(), self.get_config().get_mail_passwd_or_token())
        logging.debug('the current login user that is {0} and password that is {1}.'.format(
            self.get_config().get_mail_user(), 'the confidential data, no display'))
        logging.info('the mail initialization is ready.')
        return self

    def builderText(self, subject, content):
        ''' the default build content that is what subtype is plain and charset is utf-8 '''
        logging.debug('the generator performs the operations of building the mail subject and content...')
        builder = MIMETextBuilder(self._smtp)
        builder.set_config(self.get_config())
        builder.set_subject(subject).setContent(content).build()
        logging.debug('the generator build task complete.')
        return self

    def sendmail(self):
        ''' the send mail '''
        if self._smtp.get_mimeObj():
            logging.info('the mail sending...')
            self._smtp.sendmail(self.get_config().get_mail_sender(),
                                self.get_config().get_mail_receiver(),
                                self._smtp.get_mimeObj().as_string())
            logging.info('the mail sending task completed.')
        else:
            raise ReferenceError('the current is mime object is invaild which sending mail task that is failed.')
        return self

    def quit(self):
        ''' the send mail '''
        self._smtp.quit()
        logging.info('the current e-mail has been delivered to the other e-mail, the task is completed and exit.')

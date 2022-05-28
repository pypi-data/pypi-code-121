# -*- coding:utf-8 -*-

import logging
import os
from com.dvsnier.email import DEBUGGER

from com.dvsnier.email.callback.icallback import ICallback
from typing import Any, Dict


class Config(ICallback, object):
    '''the email config'''

    # the config information that dict typing
    _config = {}  # type: Dict[str, Any]
    # the Set up server
    _mail_host = None
    # the Server SSL default port
    _mail_port = None
    # the email user name
    _mail_user = None
    # the email Password or token
    _mail_passwd_or_token = None
    # the email Sender
    _mail_sender = None
    # the email Sender alias that optional
    _sender_alias = None
    # the email Receiver
    _mail_receiver = None
    # the email Receiver alias that optional
    _receiver_alias = None

    def __init__(self):
        super(Config, self).__init__()

    def obtain_config(self, config_file):
        """the read xxx.cfg"""
        if not config_file or not os.path.exists(config_file):
            raise FileNotFoundError('the current config path is not found.')
        logging.info('the start parsing the configuration file that is {}'.format(os.path.abspath(config_file)))
        with open(config_file) as file_handler:
            lines = file_handler.readlines()
        for line in lines:
            if line.strip().startswith('#'):
                continue  # ignore notes
            else:
                try:
                    split_at = line.index("=")
                except ValueError:
                    continue  # ignore bad/empty lines
                else:
                    self._config[line[:split_at].strip()] = line[split_at + 1:].strip()
        # logging.debug('the current config file: {}'.format(self._config))
        self.callback()
        return self._config

    def callback(self):
        super(Config, self).callback()
        self.set_mail_host(self._config.get('mail_host', None))
        self.set_mail_port(self._config.get('mail_port', None))
        self.set_mail_user(self._config.get('mail_user', None))
        self.set_mail_passwd_or_token(self._config.get('mail_passwd', None))
        self.set_mail_sender(self._config.get('mail_sender', None))
        self.set_sender_alias(self._config.get('sender_alias', None))
        self.set_mail_receiver(self._config.get('mail_receiver', None))
        self.set_receiver_alias(self._config.get('receiver_alias', None))
        logging.debug('the parsing configuration information completed.')

    def generate_config(self, config_file):
        """the read xxx.cfg"""
        self.obtain_config(config_file)
        return self

    def get_config(self):
        ''' the get config information that dict typing '''
        return self._config

    def update_config(self, config):
        ''' the update config information that dict typing '''
        if config:  # type: Config
            if config.get_mail_host():
                self.set_mail_host(config.get_mail_host())
            if config.get_mail_port():
                self.set_mail_port(config.get_mail_port())
            if config.get_mail_user():
                self.set_mail_user(config.get_mail_user())
            if config.get_mail_passwd_or_token():
                self.set_mail_passwd_or_token(config.get_mail_passwd_or_token())
            if config.get_mail_sender():
                self.set_mail_sender(config.get_mail_sender())
            if config.get_sender_alias():
                self.set_sender_alias(config.get_sender_alias())
            if config.get_mail_receiver():
                self.set_mail_receiver(config.get_mail_receiver())
            if config.get_receiver_alias():
                self.set_receiver_alias(config.get_receiver_alias())
            if DEBUGGER:
                logging.debug('the update configuration information completed.')
        return self

    def get_mail_host(self):
        ''' the get mail host '''
        return self._mail_host

    def set_mail_host(self, mail_host):
        ''' the set mail host '''
        self._mail_host = mail_host
        return self

    def get_mail_port(self):
        ''' the get mail port '''
        return self._mail_port

    def set_mail_port(self, mail_port):
        ''' the set mail port '''
        self._mail_port = mail_port
        return self

    def get_mail_user(self):
        ''' the get mail user '''
        return self._mail_user

    def set_mail_user(self, mail_user):
        ''' the set mail user '''
        self._mail_user = mail_user
        return self

    def get_mail_passwd_or_token(self):
        ''' the get mail password token'''
        return self._mail_passwd_or_token

    def set_mail_passwd_or_token(self, mail_passwd_or_token):
        ''' the set mail password or token '''
        self._mail_passwd_or_token = mail_passwd_or_token
        return self

    def get_mail_sender(self):
        ''' the get mail sender '''
        return self._mail_sender

    def set_mail_sender(self, mail_sender):
        ''' the set mail sender '''
        self._mail_sender = mail_sender
        return self

    def get_sender_alias(self):
        ''' the get sender alias'''
        return self._sender_alias

    def set_sender_alias(self, sender_alias):
        ''' the set sender alias'''
        self._sender_alias = sender_alias
        return self

    def get_mail_receiver(self):
        ''' the get mail receiver '''
        return self._mail_receiver

    def set_mail_receiver(self, mail_receiver):
        ''' the set mail receiver '''
        self._mail_receiver = mail_receiver
        return self

    def get_receiver_alias(self):
        ''' the get receiver alias '''
        return self._receiver_alias

    def set_receiver_alias(self, receiver_alias):
        ''' the set receiver alias '''
        self._receiver_alias = receiver_alias
        return self

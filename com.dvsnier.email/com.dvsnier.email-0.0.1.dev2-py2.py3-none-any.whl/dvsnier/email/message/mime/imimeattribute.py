# -*- coding:utf-8 -*-

from com.dvsnier.email.lifecycle.iconfigcycle import IConfigCycle
from com.dvsnier.email.message.mime.iattribute import IAttribute


class IMIMEAttribute(IAttribute, IConfigCycle, object):
    ''' the MIME attribute class '''

    _sender = None
    _sender_alias = None
    _receiver = None
    _receiver_alias = None

    def __init__(self):
        super(IMIMEAttribute, self).__init__()

    def onConfig(self, config):
        super(IMIMEAttribute, self).onConfig(config)
        if config:
            self._config = config
            self.onExecute()
        return self

    def onExecute(self):
        super(IMIMEAttribute, self).onExecute()
        self.set_sender(self.get_config().get_mail_sender())
        self.set_sender_alias(self.get_config().get_sender_alias())
        self.set_receiver(self.get_config().get_mail_receiver())
        self.set_receiver_alias(self.get_config().get_mail_receiver())

    def get_sender(self):
        ''' the get sender '''
        return self._sender

    def set_sender(self, sender):
        ''' the set sender '''
        self._sender = sender

    def get_sender_alias(self):
        ''' the get sender alias'''
        return self._sender_alias

    def set_sender_alias(self, sender_alias):
        ''' the set sender alias'''
        self._sender_alias = sender_alias

    def get_receiver(self):
        ''' the get receiver '''
        return self._receiver

    def set_receiver(self, receiver):
        ''' the set receiver '''
        self._receiver = receiver

    def get_receiver_alias(self):
        ''' the get receiver alias '''
        return self._receiver_alias

    def set_receiver_alias(self, receiver_alias):
        ''' the set receiver alias '''
        self._receiver_alias = receiver_alias

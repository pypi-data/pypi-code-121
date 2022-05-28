# -*- coding:utf-8 -*-

from com.dvsnier.email.message.builder.imimebuilder import IMIMEBuilder


class AbstractMIMEBuilder(IMIMEBuilder, object):
    '''the mime build class'''

    # the config instance
    _config = None
    # the dvs mime instance
    _dvsMime = None
    # the email subject
    _subject = None

    def __init__(self, smtp):
        super(AbstractMIMEBuilder, self).__init__(smtp)

    def get_config(self):
        ''' the get config information '''
        return self._config

    def set_config(self, config):
        ''' the set config information '''
        self._config = config
        return self

    def get_dvsMime(self):
        ''' the get dvsMime information '''
        return self._dvsMime

    def set_dvsMime(self, dvsMime):
        ''' the set dvsMime information '''
        self._dvsMime = dvsMime
        return self

    def get_subject(self):
        ''' the get email subject '''
        return self._subject

    def set_subject(self, subject):
        ''' the set email subject '''
        self._subject = subject
        return self

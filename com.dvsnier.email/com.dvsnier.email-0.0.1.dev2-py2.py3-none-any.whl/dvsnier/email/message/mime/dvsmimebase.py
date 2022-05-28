# -*- coding:utf-8 -*-

from com.dvsnier.email.callback.icallback import ICallback
from com.dvsnier.email.message.mime.idvsbase import IDvsBase
from com.dvsnier.email.message.mime.imimeattribute import IMIMEAttribute


class DvsMIMEBase(IDvsBase, ICallback, object):
    ''' the base MIME class '''

    _message = None
    _subject = None
    # _from = None
    # _to = None

    def __init__(self):
        super(DvsMIMEBase, self).__init__()
        self._attribute = IMIMEAttribute()

    def get_message(self):
        ''' the get message '''
        return self._message

    def set_message(self, message):
        ''' the set message '''
        self._message = message
        return self

    def get_subject(self):
        ''' the get email subject '''
        return self._subject

    def set_subject(self, subject):
        ''' the set email subject '''
        self._subject = subject
        return self

    # def get_from(self):
    #     ''' the get email from address '''
    #     return self._from

    # def set_from(self, from):
    #     ''' the set email from address '''
    #     self._from = from
    #     return self

    # def get_to(self):
    #     ''' the get email to address '''
    #     return self._to

    # def set_to(self, to):
    #     ''' the set email to address '''
    #     self._to = to
    #     return self

    def callback(self):
        return super(DvsMIMEBase, self).callback()

# -*- coding:utf-8 -*-

from com.dvsnier.email.message.mime.imimeattribute import IMIMEAttribute


class IMIMETextAttribute(IMIMEAttribute, object):
    ''' the MIME text attribute class '''

    _content = None
    _subtype = None
    _charset = None

    def __init__(self):
        super(IMIMETextAttribute, self).__init__()

    def get_content(self):
        ''' the get content '''
        return self._content

    def set_content(self, content):
        ''' the set content '''
        self._content = content

    def get_subtype(self):
        ''' the get _subtype '''
        return self._subtype

    def set_subtype(self, subtype):
        ''' the set subtype '''
        self._subtype = subtype

    def get_charset(self):
        ''' the get charset '''
        return self._charset

    def set_charset(self, charset):
        ''' the set charset '''
        self._charset = charset

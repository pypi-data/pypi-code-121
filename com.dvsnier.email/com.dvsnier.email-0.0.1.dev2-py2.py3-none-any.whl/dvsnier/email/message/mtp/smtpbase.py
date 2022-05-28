# -*- coding:utf-8 -*-


class SmtpBase(object):
    ''' the base SMTP class that is use for send email '''

    # the smtplib smtp instance
    _smtpObj = None
    # the smtplib mime instance
    _mimeObj = None

    def __init__(self):
        super(SmtpBase, self).__init__()

    def get_smtpObj(self):
        ''' the get smtp instance '''
        return self._smtpObj

    def set_smtpObj(self, smtpObj):
        ''' the set smtp instance '''
        if not smtpObj:
            raise KeyError('the smtp instance is undefined or invalid')
        self._smtpObj = smtpObj

    def get_mimeObj(self):
        ''' the get mime instance '''
        return self._mimeObj

    def set_mimeObj(self, mimeObj):
        ''' the set mime instance '''
        # if not mimeObj:
        #     raise KeyError('the mime instance is undefined or invalid')
        self._mimeObj = mimeObj

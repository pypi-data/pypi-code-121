import datetime
from enum import Enum

from TDhelper.Spider.models.Cache_L2_Model import objectId

class fingerprint(objectId):
    def __init__(self):
        super(fingerprint, self).__init__()
        self.model['fingerprint']= None
        self.model['url']= None
        self.model['lastupdatetime']= datetime.datetime.now()

    @property
    def Fingerprint(self):
        return self.model['fingerprint']

    @Fingerprint.setter
    def Fingerprint(self, value):
        self.model['fingerprint']= value

    @property
    def Url(self):
        return self.model['url']

    @Url.setter
    def Url(self, value):
        self.model['url']= value

    @property
    def LastUpdateTime(self):
        return self.model['lastupdatetime']

    @LastUpdateTime.setter
    def LastUpdateTime(self, value):
        self.model['lastupdatetime']= value
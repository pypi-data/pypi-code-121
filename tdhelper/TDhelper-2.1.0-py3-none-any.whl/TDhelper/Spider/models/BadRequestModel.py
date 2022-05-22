import datetime
from enum import Enum

from TDhelper.Spider.models.Cache_L2_Model import objectId

class BadRequest(objectId):
    def __init__(self):
        super(BadRequest, self).__init__()
        self.model['url']= None
        self.model['source']= None
        self.model['key']= None
        self.model['updatetime']= datetime.datetime.now()
    
    @property
    def Url(self):
        return self.model['url']
    @Url.setter
    def Url(self, value):
        self.model['url']= value

    @property
    def Source(self):
        return self.model['source']
    @Source.setter
    def Source(self, value):
        self.model['source']= value
    
    @property
    def Key(self):
        return self.model['key']
    @Key.setter
    def Key(self, value):
        self.model['key']= value

    @property
    def UpdateTime(self):
        return self.model['updatetime']
    @UpdateTime.setter
    def UpdateTime(self, value):
        self.model['updatetime']= value
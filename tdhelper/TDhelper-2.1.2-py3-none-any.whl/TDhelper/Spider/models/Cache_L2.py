import datetime
from enum import Enum

from TDhelper.Spider.models.Cache_L2_Model import objectId

class RecordStatus(Enum):
    '''
    地址爬取状态
    '''
    # 等待爬取
    WAIT= 0
    # 爬取中
    SPIDERING= 1
    # 爬取失败
    FAIL= 2

class L2(objectId):
    def __init__(self):
        super(L2, self).__init__()
        self.model['url']= None
        self.model['source']= None
        self.model['key']= None
        self.model['status']= RecordStatus.WAIT.value
        self.model['updatetime']= datetime.datetime.now()

    @property
    def URL(self):
        return self.model['url']

    @URL.setter
    def URL(self, value):
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
    def status(self):
        return self.model['status']

    @status.setter
    def status(self, value):
        self.model['status']= value

    @property
    def updatetime(self):
        return self.model['updatetime']

    @updatetime.setter
    def updatetime(self, value):
        self.model['updatetime']= value
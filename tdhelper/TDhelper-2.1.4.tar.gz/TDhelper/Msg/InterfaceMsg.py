from TDhelper.Msg.Config import *
from TDhelper.apiCore import *
import time
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Msg():
    '''发送信息接口
       
       Args:
       config (class<MsgConfig>): Open api config.
       sendBy (str): send person, default value is "".
    '''
    @abc.abstractclassmethod
    def __init__(self, config:Config, sendBy:str=""):
        self._config=config
        self._sendBy=sendBy
        self._sendHandle=apiCore(self._config.PlatformName,config.Version)

    @abc.abstractclassmethod
    def Send(self, sendTo:str="", sendBuff:str="", apiKey:str="send"):
        '''立即发送

           Args:
           sendTo (str): message recive person, default value {}.  
           sendBuff (str): send content, default value "". 
           apiKey (str): send api keyword,default value is "send".
        '''
    @abc.abstractclassmethod
    def MultipleSend(self,sendTo:list=[], sendBuff:str="",apiKey:str="multiplesend"):
        '''批量发送

            Args:
           sendTo (array): message recive person, default value [].  
           sendBuff (str): send content, default value "". 
           apiKey (str): multiple send api keyword,default value is "multiplesend".
        '''

    @abc.abstractclassmethod
    def Install(self):
        '''You can add the api'''

    @abc.abstractclassmethod
    def Uninstall(self):
        '''You can delete all msg api'''

from TDhelper.Msg.InterfaceMsg import *
from TDhelper.apiCore import *

class SMS(Msg):
    '''手机短信
       
       Args:
       config (class<Config>): Open api config.
       sendBy (str): set system sendby,default value is "".
    '''
    def __init__(self, config:Config, sendBy:str=""):
        super(SMS,self).__init__(config, sendBy)
        
    def Send(self, sendTo:str='', sendBuff:str='', apiKey:str="send"):
        '''Send SMS method

            Args:
                sendTo (str): SMS recvice person, default value is None.
                sendBuff (str): SMS content, default value is "", will replace params (sendby,sendto,time.localtime())
                apiKey (str): send api keyword, default value is "send".
        '''
        if sendTo:
            argsTemplete=self._sendHandle.GetArgsString(apiKey)
            if argsTemplete:
                data= argsTemplete.format(str(sendTo),sendBuff.format(self._sendBy,sendTo,time.localtime()))  #create data
                return self._sendHandle.Call(apiKey, data)  #call remote api

    def MultipleSend(self, sendTo:array=[],sendBuff:str="", apiKey:str="multiplesend"):
        '''Multiple Send SMS method
        
            Args:
                sendTo (array): SMS recvice person, default value is [].
                sendBuff (str): SMS content, default value is "", will replace params (sendby,sendto,time.localtime())
                apiKey (str): send api keyword, default value is "multiplesend".
        '''
        if sendTo:
            argsTemplete=self._sendHandle.GetArgsString(apiKey)
            if argsTemplete:
                data= argsTemplete.format(str(sendTo),sendBuff.format(self._sendBy,sendTo,time.localtime()))  #create data
                return self._sendHandle.Call(apiKey, data)  #call remote api

    def Install(self):
        '''api config'''
        for item in self._config.Apis:
            self._sendHandle.AddApi(item.Key, item.Uri, item.argsTemplete, item.Type)
        self._sendHandle.SaveToFile()

    def Unstall(self):
        '''clear all api'''
        self._sendHandle.ClearCache()
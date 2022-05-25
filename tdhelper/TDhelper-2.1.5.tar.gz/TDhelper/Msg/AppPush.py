from TDhelper.Msg.InterfaceMsg import *
from TDhelper.apiCore import *

class AppPush(Msg):
    def __init__(self):
        super(AppPush,self).__init__()

    def Send(self, sendTo='', sendBuff='', apiKey='send'):
        if sendTo:
            argsTemplete=self._sendHandle.GetArgsString(apiKey)
            if argsTemplete:
                data= argsTemplete.format(str(sendTo),sendBuff.format(self._sendBy,sendTo,time.localtime()))  #create data
                return self._sendHandle.Call("send", data)  #call remote api

    def MultipleSend(self, sendTo=[], sendBuff='', apiKey='multiplesend'):
        if sendTo:
            argsTemplete=self._sendHandle.GetArgsString(apiKey)
            if argsTemplete:
                data= argsTemplete.format(str(sendTo),sendBuff.format(self._sendBy,sendTo,time.localtime()))  #create data
                return self._sendHandle.Call("send", data)  #call remote api

    def Install(self):
        for item in self._config.Apis:
            self._sendHandle.AddApi(item.Key, item.Uri, item.argsTemplete, item.Type)
        self._sendHandle.SaveToFile()

    def Uninstall(self):
        self._sendHandle.ClearCache()
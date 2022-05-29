from TDhelper.Msg.InterfaceMsg import *
from TDhelper.apiCore import *

class EmailByApi(Msg):
    def __init__(self):
        super(EmailByApi,self).__init__()

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

class EmailByMailServer(Msg):
    def __init__(self, config, sendBy=''):
        super(EmailByMailServer,self).__init__(config, sendBy=sendBy)

    def setAccount(self, sendAccount:str, accountPWD:str, eType="pop3", certificate:str=""):
        '''设置发送帐号
            
            Args:
            sendAccount (str): send email account.
            accountPWD (str): send email account's password.
            eType (str): send type, enum(pop3,imap,smtp), default value is "pop3".
            certificate (str): (https) private certificate.
        '''
        eType=eType.lower()
        if eType == "pop3":
            pass
        elif eType == "smtp":
            pass
        elif eType== "imap":
            pass

    def Send(self, sendTo='', sendBuff='', apiKey='send'):
        #todo
        pass

    def MultipleSend(self, sendTo=[], sendBuff='', apiKey='multiplesend'):
        #todo
        pass

    def Install(self):
        pass

    def Uninstall(self):
        pass

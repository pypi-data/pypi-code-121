import threading
import re
from TDhelper.network.socket import base,SOCKET_TYPE,SOCKET_EVENT, Event,trigger,call, get_host_ip
import socket

class Client(base,threading.Thread):
    def __init__(self,ip,port,buffSize=1024,maxReconnect=5):
        threading.Thread.__init__(self)
        super(Client,self).__init__()
        if re.match(r"^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$", ip, re.I | re.M):
            ip= socket.gethostbyname(ip)
        self._max_reconnect= maxReconnect
        self._reconnect=0
        self.uri=(ip,port)
        self.__runing=threading.Event()
        self._buffSize=buffSize
        self.__state=True
        self.createsocket(SOCKET_TYPE.TCPIP)
        self.setTimeout(10)
        self.__runing.set()

    def run(self):
        self.__connection()

    @trigger("connection")
    def __connection(self):
        try:
            self.__state= True
            self.connection(self.uri)
            self._reconnect= 0
            self.on(SOCKET_EVENT.onConnection,self)
        except Exception as e:
            self.__state=False
            if self._reconnect>self._max_reconnect:
                self.on(SOCKET_EVENT.onError,e)
            else:
                self._reconnect+=1
                self.__connection()

    @trigger("send")
    def sendMsg(self,buff):
        try:
            if self.__state:
                self.send(self.getSocket(),buff)
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)

    @trigger("recv")
    def recvMsg(self):
        try:
            while self.__runing.is_set() and self.__state:      
                buff=self.recv(self.getSocket(),self._buffSize)
                if not buff:
                    self.__runing.clear()
                    break
                self.on(SOCKET_EVENT.onRecv,buff)
        except Exception as e:
            pass
            #self.on(SOCKET_EVENT.onError,e)
        finally:
            pass #self.closeClient()

    def setRuning(self):
        if self.__runing.is_set():
            self.__runing.clear()

    def closeClient(self):
        try:
            if self.__state:
                self.__state=False
                self.setRuning()
                self.close()
                #super(Client,self).close()
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)
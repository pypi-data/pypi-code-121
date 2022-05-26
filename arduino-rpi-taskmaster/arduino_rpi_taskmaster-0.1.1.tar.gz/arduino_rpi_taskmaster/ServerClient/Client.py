import socket
import time
class Client:
    """Documentation for Client

    """
    def __init__(self,port):
        self.host = None
        self.port = port
        self.client = None
    def send_data(self,ip,data):
        """This send data to the server once it take data as argument and send it to server"""
        self.client = socket.socket()
        self.client.connect((ip,self.port))
        self.client.sendall(bytes(data,"utf-8"))
        self.client.close()

import socket
import sys

def getSite(site):

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect(("24.143.57.55",7070))

    data = site

    clientSocket.send(data.encode())

    dataFromServer = clientSocket.recv(1024)
    return dataFromServer.decode()

import socket
import os


HOST = "localhost"
PORT = 8000
ADDRESS_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM
FRONTENDS_FOLDER = "frontends/"
HTML404 = os.path.abspath('socket_project/default_frontends/404.html')

import socket


class Server:
    def __init__(self,
                 host="",
                 port=12345,
                 recv=1024,
                 code="utf-8"):
        self.s = socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.recv = recv
        self.code = code

    def bind(self):
        self.s.bind((self.host, self.port))

    def listen(self):
        self.s.listen(1)
        self.conn, self.addr = self.s.accept()

    def wait_msg(self):
        data = self.conn.recv(self.recv).decode(self.code)
        return data

    def send(self, msg):
        self.conn.sendall(msg.encode())

    def close(self):
        self.conn.close()
        self.s.close()


class Client:
    def __init__(self,
                 host="",
                 port=12345,
                 recv=1024,
                 code="utf-8"):
        self.s = socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.recv = recv
        self.code = code

    def bind(self):
        self.s.connect((self.host, self.port))

    def wait_msg(self):
        data = self.s.recv(self.recv).decode(self.code)
        return data

    def send(self, msg):
        self.s.sendall(msg.encode())

    def close(self):
        self.s.close()

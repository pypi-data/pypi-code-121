import socket,json
import time

# class SocketClient:
#     def __init__(self, ip: str, port: int):
#         self.s = socket.socket()
#         self.s.connect((ip, port))
#
#     def sender(self, data: dict)->json:
#         data = json.dumps(data)
#         self.s.send(bytes(data.encode("utf-8")))
#         return json.loads(str(self.s.recv(1024), encoding="utf-8"))
#
#     def close(self):
#         self.s.close()



class SocketClient:
    def __init__(self, ip: str, port: int):
        time.sleep(2)
        self.s = socket.socket()
        self.s.connect((ip, port))
        self.recv_data = b''

    def sender(self, data: dict) -> json:
        data = json.dumps(data)
        self.s.send(bytes(data.encode("utf-8")))
        #return str(self.s.recv(1024), encoding="utf-8")
        #print(self.s.recv(1024).decode('utf-8'))
        # print(str(self.s.recv(1024), encoding="utf-8"))
        #print(self.s.recv(1024))
        #return json.loads(self.s.recv(1024))
        return json.loads(str(self.s.recv(1024), encoding="utf-8"))


    def close(self):
        self.s.close()



if __name__ == '__main__':
    socket = SocketClient('10.242.167.159',2159)
    data = {"type": "command", "module": "client"}
    data["method"] = "JoinChannle"
    data["token"] = ""
    res = socket.sender(data)
    print(res)
    socket.close()
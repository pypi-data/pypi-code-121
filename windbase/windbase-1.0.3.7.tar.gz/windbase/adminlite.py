# /*
#  * @Author: Guofeng He 
#  * @Date: 2022-05-14 08:52:33 
#  * @Last Modified by:   Guofeng He 
#  * @Last Modified time: 2022-05-14 08:52:33 
#  */

#coding=utf-8


'''
    tools 常用的工具
'''



import logging
from _thread import start_new_thread
import time

from windbase.tools import Tools
from windbase.commengine import CommEngineTCP


class AdminServer(object):

    def __init__(self, port=9000, prompt="Admin",admin_pass="password", allow_ip=["127.0.0.1"], admin_process=None):
        self.port, self.allow_ip = port, allow_ip
        self.prompt = prompt
        self.password = admin_pass
        if admin_process:
            self.admin_process = admin_process
        self.quitting = True
        self.tcp_pce = CommEngineTCP(timeout=2)

    def start(self):
        self.quitting = False
        self.sock = self.tcp_pce.initsock(bind_addr=("0.0.0.0", self.port))
        start_new_thread(self.tcp_pce.wait_accept, (self.sock, self.accept_process))
        pass

    def verify_password(self, data, addr, sock):
        if data.decode() == self.password:
            self.tcp_pce.send(sock, b"\n" + self.prompt.encode() + b">", addr)
            start_new_thread(self.tcp_pce.connection_receive, (sock, addr, self.connect_process))
            return False
        else:
            logging.warning("Error password! from %s %d." % (addr[0], addr[1]))
            sock.close()
            return False

    def accept_process(self, sock, addr):
        if addr[0] in self.allow_ip or "0.0.0.0" in self.allow_ip:
            self.tcp_pce.send(sock, b"Welcome!\nplease input your password:", addr)
            self.tcp_pce.connection_receive(sock, addr, self.verify_password)
            return True
        else:
            return False

    def connect_process(self, data, addr, sock):
        self.tcp_pce.send(sock, self.admin_process(data.decode()).encode() + b"\n" + self.prompt.encode() + b">",
                          addr)
        return True

    def admin_process(self, command):
        logging.debug("command:%s" % (command))
        return "you should define your own admin process."

    def quit(self):
        self.quitting = True
        self.tcp_pce.quit()
        self.sock.close()

    @staticmethod
    def run_daemon(config:dict,status:dict,flag:str):
        '''
        run adminserver with config, until status[falg]=True

        Args:
            config (_type_): {admin_port:9001,admin_pass:password,allow_src:127.0.0.1,admin_process:None}}
            status (_type_): _description_
            flag (_type_): _description_
        '''
        adminserver = AdminServer(port=config.get("admin_port", 9000),
                                    prompt= config.get("prompt","Admin"),
                                    admin_pass =config["admin_pass"],
                                    admin_process=config["admin_process"])
        adminserver.start()

        while not status.get(flag,False):
            time.sleep(1)
            pass
        adminserver.quit()
        status[flag] = True
        return 


class AdminClient(object):

    def __init__(self, server_addr=("127.0.0.1", 9000)):
        self.server_addr = server_addr
        self.quitting = True
        self.tcp_pce = CommEngineTCP(timeout=10)
        self.sock = self.tcp_pce.initsock()

    def start(self):
        self.quitting = False
        self.tcp_pce.connect(self.sock, self.server_addr)
        self.tcp_pce.connection_receive(self.sock, self.server_addr, self.run_command)
        pass

    def run_command(self, data, addr, sock):
        print(data.decode(), end="")
        if len(data) == 1522:  # have more data
            return True
        command = input()
        if command == "exit":
            self.quit()
            return False
        self.tcp_pce.send(sock, command.encode(), self.server_addr)
        return True

    def quit(self):
        self.quitting = True
        self.tcp_pce.quit()
        self.sock.close()




def main():
    options_dict = Tools.get_arguments({
                                "ip":{"default":"127.0.0.1","help":'adimlite ip'},
                                "port":{"default":"9000","help":'adimlite port'},
                                })
    print("welcome use admin lite. (type 'exit' to quit)")
    ip,port = options_dict.get("ip"), int(options_dict.get("port"))
    print("connect to %s %d" % (ip,port))
    client = AdminClient(server_addr=(ip,port))
    client.start()


if __name__ == '__main__':
    main()
from typing import NamedTuple

from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer


'''
server
pip installl pyftpdlib

Read permissions:
"e" = change directory (CWD, CDUP commands)
"l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE commands)
"r" = retrieve file from the server (RETR command)
Write permissions:

"a" = append data to an existing file (APPE command)
"d" = delete file or directory (DELE, RMD commands)
"f" = rename file or directory (RNFR, RNTO commands)
"m" = create directory (MKD command)
"w" = store a file to the server (STOR, STOU commands)
"M" = change file mode / permission (SITE CHMOD command) New in 0.7.0
"T" = change file modification time (SITE MFMT command) New in 1.5.3

注意Linux模式下 FTP需要使用主动模式连接 一般FTP为被动连接

'''

'''
client
tp.set_debuglevel(2)       #打开调试级别2，显示详细信息
ftp.set_pasv(0)           #0主动模式 1 #被动模式
print ftp.getwelcome()      #打印出欢迎信息
ftp.cmd("xxx/xxx")         #更改远程目录
ftp.set_debuglevel(0)       #关闭调试模式
ftp.quit()              #退出ftp
ftp.dir()               #显示目录下文件信息
ftp.mkd(pathname)          #新建远程目录
ftp.pwd()               #返回当前所在位置
ftp.rmd(dirname)          #删除远程目录
ftp.delete(filename)        #删除远程文件
ftp.rename(fromname, toname)   #将fromname修改名称为toname。
'''

class FTPEventHandler(FTPHandler):

    def on_connect(self):
        pass

    def on_disconnect(self):
        # do something when client disconnects
        pass

    def on_login(self, username):
        # do something when user login
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        pass

    def on_file_received(self, file):
        # do something when a file has been received
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        pass

class FtpConfig(NamedTuple):
    HOST: str
    PORT: int
    USER: str = ''
    PSW: str = ''
    USERS: list = []        #用户列表
    ANONY_MOUS: str = ''    #匿名路径
    UPLOAD_SPEED: int = 300*1024        #上传速度
    DOWN_SPEED: int = 300*1024        #下载速度
    CONNECT_LIMIT: int = 150        #最大连接数
    PER_IP_LIMIT: int = 10          #单个ip最大连接数
    PASSIVE_PORTS: tuple = (2000, 2200)        #被动端口范围
    ENABLE_LOG: int = 0
    WELCOME: str = 'Welcome to my ftp'    #欢迎信息
    DEBUG_LEVEL: int = 0
    BUFFER_SIZE: int = 8192

class FtpAccessor:

    def __init__(self, config: FtpConfig):
        self.config = config
        self.server = None

    def __del__(self):
        self.close_server()

    def exit(self):
        self.close_server()

    #启动客户端
    def get_client(self):
        client = FTP()
        client.set_debuglevel(self.config.DEBUG_LEVEL)
        client.connect(self.config.HOST, self.config.PORT)
        if len(self.config.USER) > 0:
            client.login(self.config.USER, self.config.PSW)
        return client

    #启动服务器
    def start_server(self):
        authorizer = DummyAuthorizer()
        for user in self.config.USERS:
            authorizer.add_user(user.get('name'), user.get('psw'), user.get('folder'), user.get('role'))
        if len(self.config.ANONY_MOUS) > 0:
            authorizer.add_anonymous(self.config.ANONY_MOUS)

        throttled = ThrottledDTPHandler
        throttled.read_limit = self.config.DOWN_SPEED
        throttled.write_limit = self.config.DOWN_SPEED

        handler = FTPEventHandler
        handler.authorizer = authorizer
        handler.banner = self.config.WELCOME
        handler.passive_ports = range(self.config.PASSIVE_PORTS[0], self.config.PASSIVE_PORTS[1])

        self.server = FTPServer((self.config.HOST, self.config.PORT), handler)
        self.server.max_cons = self.config.CONNECT_LIMIT
        self.server.max_cons_per_ip = self.config.PER_IP_LIMIT

        self.server.serve_forever()

    def close_client(self, client):
        if client is not None:
            client.quit()

    def close_server(self):
        if self.server is not None:
            self.server.close_all()

    #切换目录
    def cwd_folder(self, client: FTP, remote_file_folder: str):
        if len(remote_file_folder) > 0:
            result = client.cwd(remote_file_folder)

    #下载文件
    def download_file(self, client: FTP, remote_file_name: str, local_file_path: str, remote_file_folder: str=''):
        self.cwd_folder(client, remote_file_folder)
        result = client.retrbinary(f"RETR {remote_file_name}", open(local_file_path, 'wb').write, self.config.BUFFER_SIZE)
        if result.startswith('226'):
            return True
        raise Exception(f"download fail({result})")

    #上传文件
    def upload_file(self, client: FTP, remote_file_name: str, local_file_path: str, remote_file_folder: str=''):
        self.cwd_folder(client, remote_file_folder)
        result = client.storbinary(f"STOR {remote_file_name}", open(local_file_path, 'rb'), self.config.BUFFER_SIZE)
        if result.startswith('226'):
            return True
        raise Exception(f"upload fail({result})")

    #获取用户列表
    def get_users(self):
        return self.config.USERS

    #更新用户
    def update_users(self, users: list):
        for user in self.config.USERS:
            if self.server.handler.authorizer.has_user(user.get('name')) is True:
                self.server.handler.authorizer.remove_user(user.get('name'))

        self.config = self.config._replace(USERS=users)

        for user in self.config.USERS:
            self.server.handler.authorizer.add_user(user.get('name'), user.get('psw'), user.get('folder'), user.get('role'))

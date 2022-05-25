# coding:utf-8
import paramiko
import os
import time


class SSHConn:
    """ 维护一个基于ssh协议的linux连接 """

    def connect(self, host, port, user, pwd):
        """ 给入连接信息初始化该连接 """
        self.close()
        self.transport = paramiko.Transport(host, port)
        self.transport.connect(username=user, password=pwd)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, port, user, pwd, timeout=3)
        time.sleep(1)
        return self

    def exec_command(self, cmd):
        """ 执行单一命令，返回结果 """
        stdout = self.client.exec_command(cmd)[1]
        return stdout.read().decode("UTF-8").strip()

    def exec_script(self, script):
        """ 执行shell脚本（如果给入是一个路径则读取这个文件内容作为脚本执行），返回交互式shell内容 """
        if os.path.exists(script):
            file = open(script)
            script = file.read()
            file.close()
            
        mess = ''
        shell = self.client.invoke_shell()
        shell.send(script + '\n')
        shell.send('exit\n')
        while not shell.exit_status_ready():
            out = mess + shell.recv(1024).decode('UTF-8')
        shell.close()
        return out
        
    def _download(self, src, dst):
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        filetype = self.exec("ls -ld " + src)[0]
        if filetype == '-':
            sftp.get(src, dst)
        elif filetype == 'd':
            for file in sftp.listdir(src):
                self._download(src + '/' + file, dst + '/' + file)
        sftp.close()

    def download(self, src, dst):
        """ 下载文件到本地，dst只能是一个目录，表示下载到该目录下 """
        if not os.path.exists(dst):
            os.makedirs(dst)
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        filetype = self.exec("ls -ld " + src)[0]
        if filetype == '-':
            sftp.get(src, dst + '/' + src.split('/')[-1])
        elif filetype == 'd':
            self._download(src, dst)
        sftp.close()

    def close(self):
        try:
            self.client.close()
        except:
            pass
        
    def __del__(self):
        self.close()

import os
import socket
import threading
import time
import traceback
from ftplib import FTP

import socks


class BaseFtp(object):
    def __init__(self, encoding='utf-8'):
        self.ftp = FTP()
        self.ftp.encoding = encoding

    def set_proxy_socks(self, type, ip, port):
        """
        type = socks.PROXY_TYPE_SOCKS5
        :param type:
        :param ip:
        :param port:
        :return:
        """
        socks.set_default_proxy(type, ip, port)
        socket.socket = socks.socksocket
        return self

    def conn_ftp(self, ftp_host, port=21):
        self.ftp.connect(ftp_host, port)
        return self

    def login(self, username, passwd):
        self.ftp.login(username, passwd)
        return self

    def set_conn_login_pare(self, ftp_host, port, username, passwd):
        """
        设置参数
        :return:
        """
        self.ftp_host = ftp_host
        self.port = port
        self.username = username
        self.passwd = passwd
        return self

    def conn_and_login(self):
        self.conn_ftp(self.ftp_host, self.port)
        self.login(self.username, self.passwd)
        return self

    def cwd(self, dir):
        """
        更改到目录
        :param dires:
        :return:
        """
        return self.ftp.cwd(dir)  # change remote work dir

    def pwd(self):
        """
        返回当前FTP操作的路径
        :return:
        """
        return self.ftp.pwd()

    def size(self, remotefile):
        return self.ftp.size(remotefile)

    def voidcmd(self, cmd):
        """
        和FTP.sendcmd(command)功能相似，但返回代码不在200-299之间时抛出异常
        FTP.sendcmd(command):向服务器发送一条简单的FTP命令，返回响应结果
        'TYPE I'
        f"MDTM {ftp_path}" 获取时间
        :return:
        """
        return self.ftp.voidcmd(cmd)

    def retrlines(self, cmd, callback=None):
        """
        返回list的数据格式为liunx权限的格式
        dr-x------   3 user group            0 Jan 26 11:10 CN-IC-DECO-RE 中国集成电路布图设计复审撤销案件数据
        :param cmd: RETR、LIST或NLST命令
        LIST以列表形式检索有关文件及其详细信息。NLST只是以列表展示文件名
        RETR 下载
        MLSD: 更好的信息展示
        :param callback: 一个被调用的可选的单个参数,为每一行去掉后面的CRLF
        比如放入列表 可以传入
        filelist = []
        filelist.append
        :return:
        """
        return self.ftp.retrlines(cmd, callback)

    def set_pasv(self, val):
        """
        val：为True时，启用被动模式；反之，禁用。默认情况下是被动模式
        :param val:
        :return:
        """
        return self.ftp.set_pasv(val)

    def get_file_info(self, file_str):
        """
        将str 转换成字典
        :param file_str:
        :return:
        """
        dicts = {}
        dicts["time"] = []
        dicts["filename"] = []
        lists = file_str.split()
        count = 0
        for item in lists:
            item = item.strip()
            if item != "" and count <= 8:
                count = count + 1
                if count == 1:
                    # 文件属性字段
                    """
                    文件属性字段总共有10个字母组成；第一个字符代表文件的类型。
                    字母“-”表示该文件是一个普通文件
                    字母“d”表示该文件是一个目录，字母"d"，是dirtectory(目录)的缩写
                    注意：目录或者是特殊文件，这个特殊文件存放其他文件或目录的相关信息
                    字母“l”表示该文件是一个链接文件。字母"l"是link(链接)的缩写，类似于windows下的快捷方式
                    字母“b”的表示块设备文件(block)，一般置于/dev目录下，设备文件是普通文件和程序访问硬件设备的入口，是很特殊的文件。没有文件大小，只有一个主设备号和一个辅设备号。一次传输数据为一整块的被称为块设备，如硬盘、光盘等。最小数据传输单位为一个数据块(通常一个数据块的大小为512字节)
                    字母为“c”表示该文件是一个字符设备文件(character)，一般置于/dev目录下，一次传输一个字节的设备被称为字符设备，如键盘、字符终端等，传输数据的最小单位为一个字节。
                    字母为“p”表示该文件为命令管道文件。与shell编程有关的文件。
                    字母“s”表示该文件为sock文件。与shell编程有关的文件。
                    """
                    dicts["file_info"] = item
                if count == 2:
                    # 文件硬链接数 如果是一个目录，则第2字段表示该目录所含子目录的个数。
                    dicts["file_hardlink_num"] = item
                if count == 3:
                    dicts["user"] = item
                if count == 4:
                    dicts["group"] = item

                if count == 5:
                    # 文件所占用的空间(以字节为单位)
                    dicts["size"] = item

                if count in (6, 7, 8):
                    # 件（目录）最近访问（修改）时间
                    dicts["time"].append(item)
                    if count == 8:
                        count = count + 1
            else:
                dicts["filename"].append(item)

        dicts["filename"] = " ".join(dicts["filename"])
        dicts["time"] = " ".join(dicts["time"])
        return dicts

    def get_file_info_MLSD(self, file_str):
        """
        MLSD 模式下转换为字典
        :param file_str:
        :return:
        """
        dicts = {}
        lists = file_str.split(";")
        dicts["size"] = lists[0].replace("Size=", "")
        dicts["time"] = lists[1].replace("Modify=", "")
        dicts["type"] = lists[2].replace("Type=", "")
        dicts["filename"] = lists[3][1:]
        return dicts

    def down_file(self, ftp_path, local_path, blocksize=1024):
        """
        下载一个文件
        :return:
        """
        local_file_size = 0
        if os.path.exists(local_path):
            local_file_size = os.path.getsize(local_path)
        try:
            ftp_file_size = self.size(ftp_path)
            # TYPE I表示以二进制模式传输
            self.voidcmd('TYPE I')
            # 下载ftp 目标文件 local_file_size 需要跳过的size
            conn = self.ftp.transfercmd('RETR ' + ftp_path, local_file_size)
            with open(local_path, 'ab+') as file:
                if local_file_size == 0 or local_file_size > ftp_file_size:
                    file.truncate()
                recv_num = 0
                # 次数
                times = 0
                while True:
                    data = conn.recv(blocksize)
                    times = times + 1
                    recv_num = recv_num + len(data)
                    if times >= 1000:
                        print("P/T {}:{} Time {}".format(os.getpid(), threading.get_ident(),
                                                         time.strftime('%Y-%m-%d %H:%M:%S',
                                                                       time.localtime(time.time()))), recv_num)
                        times = 0
                        recv_num = 0
                    if not data:
                        break
                    file.write(data)
            # 此命令不产生什么实际动作，它仅使服务器返回OK。
            result = self.voidcmd('NOOP')
            print(result)
            # 期待以“2”开头的回复
            result = self.ftp.voidresp()
            print(result)
            return True
        except:
            self.ftp.quit()
            traceback.print_exc()
            return False

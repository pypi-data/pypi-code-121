# -*- coding: utf-8 -*-
# @Time    : 2020/11/27 16:38
# @Author  : suhong
# @File    : smb_test.py
# @Software: PyCharm
# !/usr/local/bin/python3
import os
import socket
import sys
import traceback

import fs.smbfs
from nmb.NetBIOS import NetBIOS
from smb import smb_structs
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

from re_common.baselibrary import IniConfig
from re_common.baselibrary.utils.basedir import BaseDir


# 有的smb使用fs.smbfs无法访问，可以使用smb.SMBConnection

class BaseSmb(object):
    """
    fs.smbfs 建立在 pysmb 之上
    host属性中直接输入ip无效，报错fs.errors.CreateFailed: could not get IP/host pair from '*.*.*.193'，
    包的作者目前也没有解决这个问题。加入主机名正常使用
    """

    def __init__(self, host=None, username=None, password=None,port=139,domain=""):
        self.conn = None
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.domain = domain


    def set_uri(self, uri):
        """
        'smb://username:password@SAMBAHOSTNAME:port/share'
        由于不知道如何给SAMBAHOSTNAME这个参数，尝试了没有成功
        :return:
        """
        smb_fs = fs.open_fs(uri)
        return smb_fs

    def set_default(self):
        """
        调用该函数默认链接177
        :return:
        """
        # host必须是(servername,ip),不能只提供ip，servername错误一样有效
        self.host = ("VIPS-001", "192.168.31.184")
        self.username = "caiji_smb_rw"
        self.password = "5joH9yST"
        self.port = 139
        self.domain = ""

    def set_config(self, path, sesc):
        dictsall = IniConfig(path).builder().get_config_dict()
        dicts = dictsall[sesc]
        self.host = dicts['host']
        self.username = dicts['username']
        self.password = dicts['password']
        self.port = dicts['port']
        self.domain = dicts['domain']

    def connect(self):
        """
        设置用户名 密码 进行连接
        :return:
        """
        self.conn = fs.smbfs.SMBFS(host=self.host, username=self.username,
                                   passwd=self.password,
                                   port=self.port,
                                   domain=self.domain)

    def close(self):
        # 关闭链接
        self.conn.close()

    def get_gen_dir(self):
        """
        获取根目录下的文件名
        :return:
        """
        for g in self.conn.listdir(""):
            yield g

    def is_exists(self, pathdir):
        """
        目录是否存在
        :param sPth:
        :return:
        """
        return self.conn.exists(pathdir)

    def is_dir(self, pathdir):
        """
        是否是目录
        :param sPth:
        :return:
        """
        return self.conn.isdir(pathdir)

    def is_file(self, pathfile):
        """
        是否是文件
        :param sPth:
        :return:
        """
        return self.conn.isfile(pathfile)

    def create_dir(self, pathdir):
        """
        创建目录 该方法可以创建多级目录
        :param pathdir:
        :return:
        """
        if not self.is_exists(pathdir):
            self.conn.makedirs(pathdir)

    def get_file_size(self, path):
        """
        获取文件大小
        :param path:
        :return:
        """
        size = 0
        size += self.conn.getsize(path)
        return size

    def download_file(self, srcpath, dstpath):
        """
        下载smb服务器文件到本地
        :param srcpath:本地文件
        :param dstpath: 服务器文件
        :return:
        """
        BaseDir.create_dir(srcpath)
        with open(dstpath, 'wb') as write_file:
            self.conn.download(srcpath, write_file)

    def upload_file(self, srcpath, dstpath):
        """
        上传本地文件到smb服务器文件
        :param srcpath:本地文件
        :param dstpath: 服务器文件
        :return:
        """
        self.create_dir(dstpath)
        with open(srcpath, 'rb') as read_file:
            self.conn.upload(dstpath, read_file)

    def copy_file_to_file_smb(self, filePath, tarPath, overwrite=False):
        """
        该方法只适合smb服务器地址到smb服务器地址
        :param filePath:  文件路径
        :param tarPath: 输出文件路径
        :return:
        """
        assert self.is_exists(filePath), FileNotFoundError("需要copy的文件不存在")
        assert self.conn.isfile(filePath), FileNotFoundError("需要copy的不是一个文件")

        self.conn.copy(filePath, tarPath, overwrite=overwrite)

    def copy_dir_to_dir_smb(self, oldDir, newDir, moudle=0):
        """
        该方法只适合smb服务器地址到smb服务器地址
        olddir和newdir都只能是目录，且newdir必须不存在
        :param oldDir:
        :param newDir:
        :return:
        """
        assert self.is_exists(oldDir), IsADirectoryError(oldDir + "目录不存在")
        assert not self.is_exists(newDir), IsADirectoryError(newDir + "目录存在")
        self.conn.copydir(oldDir, newDir)

    def move_file_to_file_smb(self, src_path, dst_path, overwrite=False):

        assert self.is_exists(src_path), FileNotFoundError("需要move的文件不存在")
        assert self.is_file(dst_path), FileNotFoundError("需要move的不是一个文件")
        self.conn.move(src_path, dst_path, overwrite=overwrite)

    def move_dir_to_dir_smb(self, oldDir, newDir, moudle=0):
        """
        该方法只适合smb服务器地址到smb服务器地址
        olddir和newdir都只能是目录，且newdir必须不存在
        :param oldDir:
        :param newDir:
        :return:
        """
        assert self.is_exists(oldDir), IsADirectoryError(oldDir + "目录不存在")
        assert not self.is_exists(newDir), IsADirectoryError(newDir + "目录存在")
        self.conn.movedir(oldDir, newDir)

    def delete_dir(self, dirpath):
        """
        递归删除smb服务器文件夹
        :param dirpath:
        :return:
        """
        assert self.is_file(dirpath), FileExistsError("该目录是个文件")

        self.conn.removetree(dirpath)

    def delete_file(self, filepath):
        """
       删除smb服务器文件
       :param dirpath:
       :return:
       """
        assert not self.is_file(filepath), FileNotFoundError("该路径不是个文件")

        self.conn.remove(filepath)

    def read_file(self, path, mode="r", return_model="yield"):
        """
        :param mode:
        :param path: caiji/except_client_try.txt
        :return:
        """
        with self.conn.open(path, mode, encoding="utf-8") as f:
            if return_model == "yield":
                for fLine in f:
                    yield fLine.strip()
            if return_model == "all":
                return f.read()

    def write_file(self, path, value, mode="w"):
        with self.conn.open(path, mode, encoding="utf-8") as f:
            f.write(value)


class SmbClient(object):
    """
    优缺点：函数功能丰富，文件下载功能只对普通文件如txt,dat,csv有效，压缩文件无效
    """

    def __init__(self, username, password, my_name, remote_name, ip, port=139, domain='', server_name='caiji'):
        self.username = username
        self.password = password
        self.my_name = my_name
        self.ip = ip
        self.port = port
        self.remote_name = remote_name
        self.conn = None
        self.domain = domain
        self.server_name = server_name

    def set_use_smb2(self, is_use=True):
        """
        在 pysmb 中禁用 SMB2 协议，请在创建SMBConnection实例之前将smb_structs模块中
        的SUPPORT_SMB2标志设置为False
        :param is_use:
        :return:
        """
        smb_structs.SUPPORT_SMB2 = is_use

    def get_bios_name(self, timeout=10):
        """
        想通过ip获取对应计算机名，但没有成功
        """
        bios = None
        try:
            bios = NetBIOS()
            srv_name = bios.queryIPForName(self.ip, timeout=timeout)
            print(srv_name)
            return srv_name
        except:
            traceback.print_exc()
            print(sys.stderr, "Looking up timeout, check remote_smb_ip again!!")
        finally:
            if bios is not None:
                bios.close()
            return []

    def set_config(self, path, sesc):
        dictsall = IniConfig(path).builder().get_config_dict()
        dicts = dictsall[sesc]
        self.ip = dicts['ip']
        self.port = dicts['port']
        self.username = dicts['username']
        self.password = dicts['password']
        self.my_name = dicts['my_name']
        self.remote_name = dicts['remote_name']
        self.domain = dicts['domain']

    def connect(self):
        """
        建立smb服务连接
        port: 445或者139
        :return:
        """
        try:
            self.conn = SMBConnection(self.username, self.password, self.my_name,
                                      self.remote_name,
                                      domain=self.domain)
            self.conn.connect(self.ip, self.port)
            status = self.conn.auth_result
        except:
            self.conn.close()
            status = False
        return status

    def all_shares_name(self):
        """
        列出smb服务器下的所有共享目录
        :return:
        """
        share_names = list()
        sharelist = self.conn.listShares()
        for s in sharelist:
            share_names.append(s.name)
        return share_names

    def all_file_names_in_dir(self, service_name, dir_name):
        """
        列出文件夹内所有文件名
        :param service_name: 服务名（smb中的文件夹名，一级目录）
        :param dir_name: 二级目录及以下的文件目录
        :return:
        """
        f_names = list()
        for e in self.conn.listPath(service_name, dir_name):
            if e.filename[0] != '.':  # （会返回一些.的文件，需要过滤）
                f_names.append(e.filename)
        return f_names

    def get_last_updatetime(self, service_name, file_path):
        '''
        返回samba server上的文件更新时间（时间戳），如果出现OperationFailure说明无此文件，返回0
        :param samba:
        :param service_name:
        :param file_path:
        :return:
        '''
        try:
            sharedfile_obj = self.conn.getAttributes(service_name, file_path)
            return sharedfile_obj.last_write_time
        except OperationFailure:
            return 0

    def download(self, f_names, service_name, smb_dir, local_dir):
        """
        下载文件
        :param f_names:文件名
        :param service_name:服务名（smb中的文件夹名）
        :param smb_dir: smb文件夹
        :param local_dir: 本地文件夹
        :return:
        """
        assert isinstance(f_names, list)
        for f_name in f_names:
            f = open(os.path.join(local_dir, f_name), 'wb')
            self.conn.retrieveFile(service_name, os.path.join(smb_dir, f_name), f)
            f.close()

    def createDir(self, service_name, path):
        """
        创建文件夹
        :param samba:
        :param service_name:
        :param path:
        :return:
        """
        try:
            self.conn.createDirectory(service_name, path)
        except OperationFailure:
            pass

    def upload(self, service_name, smb_dir, local_dir, f_names):
        """
        上传文件
        :param samba:
        :param service_name:服务名（smb中的文件夹名）
        :param smb_dir: smb文件夹
        :param local_dir: 本地文件列表所在目录
        :param f_names: 本地文件列表
        :return:
        """
        assert isinstance(f_names, list)
        for f_name in f_names:
            f = open(os.path.join(local_dir, f_name), 'rb')
            self.conn.storeFile(service_name, os.path.join(smb_dir, f_name), f)  # 第二个参数path包含文件全路径
            f.close()


# if __name__ == '__main__':
#     bs = BaseSmb()
#     # bs.set_uri("smb://caiji_smb_rw:5joH9yST@('VIPS-001','192.168.31.184'):139/caiji/except_client_try.txt")
#     bs.set_default()
#     bs.connect()
#     bs.write_file("caiji/except_client_try.txt","aaaa")
#     # for i in bs.get_gen_dir():
#     #     print(i)
#     # print(bs.delete_dir("down_data/test.txt"))

# if __name__ == '__main__':
#     sc = SmbClient("caiji_smb_rw", "5joH9yST", "TEST","VIPS-001", "192.168.31.184", 139, "WorkGroup")
#     sc.connect()

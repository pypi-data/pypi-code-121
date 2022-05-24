import os
import sys
import time

from pyhdfs import HdfsClient


class BaseHDFS(object):

    def __init__(self):
        self.hdfsdir = ""
        self.localdir = ""
        self.namenode = ""
        self.user_name = ""
        self.total = 0
        self.client = None
        self.FileSize = 0
        self.FailedList = list()  # 失败文件列表
        self.StartTime = time.time()

    def get_client(self):
        self.client = HdfsClient(hosts=self.namenode, user_name=self.user_name)

    def mk_hdfs_dirs(self, path):
        """
        创建目录 目录存在创建不会报错 目录里文件不会被删除

        :return:
        """

        return self.client.mkdirs(path)

    def exists(self, path):
        """
        判断路径是否存在
        :return:
        """
        return self.client.exists(path)

    def get_all_files_num(self):
        """
        获取目录下所有文件数量
        :return:
        """
        assert isinstance(self.client, HdfsClient)
        total = 0
        # 先遍历一遍，得到总文件个数
        for parent, dirnames, filenames in self.client.walk(self.hdfsdir):
            for filename in filenames:
                total += 1
        self.total = total
        return total

    def get_all_files(self):
        assert isinstance(self.client, HdfsClient)
        processed = 0
        for parent, dirnames, filenames in self.client.walk(self.hdfsdir):
            for filename in filenames:
                srcFile = '%s/%s' % (parent, filename)
                relPath = srcFile[len(self.hdfsdir) + 1:].replace('/', '\\')  # 相对于根目录的路径
                dstFile = os.path.join(self.localdir, relPath)
                if not self.down_proc_one(srcFile, dstFile):
                    self.FailedList.append(srcFile)
                processed += 1
                print('%s:' % self.hdfsdir)
                print('%d/%d/%d, time cost: %.2f s' % (
                    self.total, processed, len(self.FailedList), time.time() - self.StartTime))
                print('%d B, %.2f MB/s \n' % (
                    self.FileSize, self.FileSize / 1024 / 1024 / (time.time() - self.StartTime)))

    def down_proc_one(self, srcFile, dstFile):
        print('ProcOne \n%s\n -> \n%s ' % (srcFile, dstFile))
        dstDir = os.path.dirname(dstFile)
        if not os.path.exists(dstDir):
            os.makedirs(dstDir)

        # 目标文件已经存在且大小相同
        if os.path.exists(dstFile) and \
                (os.path.getsize(dstFile) == self.client.list_status(srcFile)[0].length):
            print('file exists: %s ' % dstFile)
            return True

        # 注意，如果已存在会被覆盖
        self.client.copy_to_local(srcFile, dstFile, overwrite=True)

        if os.path.getsize(dstFile) != self.client.list_status(srcFile)[0].length:  # 校验文件大小
            return False

        self.FileSize += os.path.getsize(dstFile)
        return True

    # 处理一个
    def up_proc_one(self, client, srcFile, dstFile):
        print('ProcOne \n%s\n -> \n%s ' % (srcFile, dstFile))

        # 目标文件已经存在且大小相同
        if client.exists(dstFile) and \
                (os.path.getsize(srcFile) == client.list_status(dstFile)[0].length):
            print('file exists: %s ' % dstFile)
            return True

        # 注意，如果已存在会被覆盖
        client.copy_from_local(srcFile, dstFile, overwrite=True)

        if os.path.getsize(srcFile) == client.list_status(dstFile)[0].length:  # 校验文件大小
            self.FileSize += os.path.getsize(srcFile)
            return True

        return False

    # 处理所有
    def up_all_files(self):
        assert isinstance(self.client, HdfsClient)
        if not self.client.exists(self.hdfsdir):
            print(self.hdfsdir + ' not found')
            sys.exit(-1)
        total = len(os.listdir(self.localdir))
        processed = 0
        for filename in os.listdir(self.localdir):
            srcFile = os.path.join(self.localdir, filename)
            dstFile = self.hdfsdir + '/' + filename
            if not self.up_proc_one(self.client, srcFile, dstFile):
                self.FailedList.append(srcFile)
            processed += 1
            print(
                '%d/%d/%d, time cost: %.2f s' % (total, processed, len(self.FailedList), time.time() - self.StartTime))
            print('%d B, %.2f MB/s \n' % (self.FileSize, self.FileSize / 1024 / 1024 / (time.time() - self.StartTime)))

        if self.FailedList:
            print('failedList: %s' % repr(self.FailedList))
        else:
            print('Good! No Error!')
            print('%d B, %.2f MB, %.2f GB, %.2f MB/s' % \
                  (self.FileSize, self.FileSize / 1024 / 1024, self.FileSize / 1024 / 1024 / 1024,
                   self.FileSize / 1024 / 1024 / (time.time() - self.StartTime)))

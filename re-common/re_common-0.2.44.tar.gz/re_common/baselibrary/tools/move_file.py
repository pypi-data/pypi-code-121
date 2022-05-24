import time

from re_common.baselibrary.mthread.MThreadingRun import MThreadingRun2
from re_common.baselibrary.mthread.mythreading import ThreadInfo
from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile
from re_common.baselibrary.utils.basequeue import BaseQueue
from re_common.facade.now import get_streamlogger, get_filelogger


def copy_one_file(fullname, sources_path, dst_path):
    """
    复制文件 不会删除
    :param fullname:
    :param sources_path:
    :param dst_path:
    :return:
    """
    fullname_size = BaseFile.get_file_size(fullname)
    # 替换前面的路径得到新文件的路劲
    dst_file = fullname.replace(sources_path, dst_path)
    # 目录不存在就创建目录
    dst_dir = BaseDir.get_file_dir_absolute(dst_file)
    BaseDir.create_dir(dst_dir)

    if BaseFile.is_file_exists(dst_file):
        dst_dir_size = BaseFile.get_file_size(dst_file)
        if fullname_size == dst_dir_size:
            return True
    # 复制文件
    BaseFile.copy_file_to_file(fullname, dst_file)
    dst_dir_size = BaseFile.get_file_size(dst_file)
    # 文件大小一致才删除源文件
    # 大小一致性对比不能用于windows 和 liunx之间的传输，两者会存在差异性
    print(fullname_size,dst_dir_size)
    if fullname_size == dst_dir_size:
        return True
    else:
        return False


def move_one_file(fullname, sources_path, dst_path):
    """
    移动文件，会删除源文件
    :param fullname:
    :param sources_path:
    :param dst_path:
    :return:
    """
    fullname_size = BaseFile.get_file_size(fullname)
    # 替换前面的路径得到新文件的路劲
    dst_file = fullname.replace(sources_path, dst_path)
    # 目录不存在就创建目录
    dst_dir = BaseDir.get_file_dir_absolute(dst_file)
    BaseDir.create_dir(dst_dir)
    if BaseFile.is_file_exists(dst_file):
        dst_dir_size = BaseFile.get_file_size(dst_file)
        if fullname_size == dst_dir_size:
            BaseFile.remove_file(fullname)
    # 复制文件
    BaseFile.copy_file_to_file(fullname, dst_file)
    dst_dir_size = BaseFile.get_file_size(dst_file)
    # 文件大小一致才删除源文件
    if fullname_size == dst_dir_size:
        BaseFile.remove_file(fullname)


def move_file(sources_path, dst_path):
    """
    移动文件，会删除源文件
    :param sources_path:
    :param dst_path:
    :return:
    """
    k = 0
    for fullname in BaseDir.get_dir_all_files(sources_path):
        k += 1
        move_one_file(fullname, sources_path, dst_path)
        if k % 1000 == 0:
            print("已经拷贝{}个文件".format(k))
    print("已经拷贝{}个文件".format(k))


class MoveFile(object):

    def __init__(self):
        self.sources_path = ''
        self.dst_path = ''


class MoveFileThread(MThreadingRun2):
    def __init__(self, num, mf):
        super(MoveFileThread, self).__init__(num)
        self.mf = mf
        self.k = 0
        self.file_logger = get_filelogger(r"F:\fun2\log")
        self.thread_pool.work_queue = BaseQueue(1000)

    def create_dir(self):
        """
        先创建所有目录,防止在多线程中创建目录冲突
        :return:
        """
        for dir in BaseDir.get_dir_all_dir(self.mf.sources_path):
            new_dir = dir.replace(self.mf.sources_path, self.mf.dst_path)
            print(new_dir)
            BaseDir.create_dir(new_dir)

    def set_task(self, threadval, *args, **kwargs):
        self.create_dir()
        for fullname in BaseDir.get_dir_all_files(self.mf.sources_path):
            self.k = self.k + 1
            self.add_job(self.func, fullname)
            if self.k % 1000 == 0:
                print("已经拷贝{}个文件".format(self.k))
        while self.get_thread_stat():
            time.sleep(1)

    def get_thread_stat(self):
        """
        如果是False代表所有的线程都在等待任务，说明所有工作都已经完成
        :return:
        """
        for k, v in self.thread_pool.thread_pool_dicts.items():
            threadinfo = v
            thread = threadinfo.get_thread()
            if thread.runstatus is not False:
                return True
        return False

    def deal_results(self, threadval, *args, **kwargs):
        time.sleep(60)

    def setProxy(self, threadval, proxysList=None):
        time.sleep(60)

    def is_break(self):
        time.sleep(5)
        if self.thread_pool.work_queue.is_empty() and self.thread_pool.result_queue.is_empty() and not self.get_thread_stat():
            for k, v in self.thread_pool.thread_pool_dicts.items():
                if k == self.etn.taskthreadname:
                    threadinfo = v
                    thread = threadinfo.get_thread()
                    if thread.is_alive():
                        return False
            return True
        else:
            return False

    def thread_pool_hook(self, threadinfo: ThreadInfo):
        # 设置代理线程不重启，默认会重启
        if threadinfo.get_thread_name() == self.etn.taskthreadname:
            threadinfo.set_is_restart(False)
        return {}

    def fun(self, threadval, *args, **kwargs):
        fullname = args[0]
        copy_one_file(fullname, self.mf.sources_path, self.mf.dst_path)
            # self.file_logger.info(fullname + "\n")


if __name__ == "__main__":
    mf = MoveFile()
    mf.sources_path = r"F:\fun2\test_gif"
    # mf.dst_path = r"F:\fun2\test_gif2"
    mf.dst_path = r"\\192.168.31.123\home\cjvip\qinym\soopat\image"
    # mf.dst_path = r"\\192.168.31.177\down_data\test"

    mft = MoveFileThread(30, mf)
    mft.run()

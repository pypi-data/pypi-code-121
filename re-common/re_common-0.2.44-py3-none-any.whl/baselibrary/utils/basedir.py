import os
import shutil
import warnings

from re_common.baselibrary.utils.basefile import BaseFile


class BaseDir(object):

    @classmethod
    def get_dir_all_files(cls, path):
        """
        返回所有的文件 不会返回目录 目的是得到一个文件列表
        # 这里注意topdown参数。
        # topdown决定遍历的顺序，
        # 如果topdown为True，则先列举top下的目录，然后是目录的目录，依次类推；
        # 反之，则先递归列举出最深层的子目录，然后是其兄弟目录，然后父目录。
        # 我们需要先修改深层的子目录
        :param path:  给定一个路径 如 C:/Users/XD/Pictures/所有视频/
        :return:
        """
        # 遍历子目录
        assert cls.is_dir(path), NotADirectoryError(path + " not is a dir please check")
        for path, dirNames, fileNames in os.walk(path, topdown=True):
            # 获取当前目录的所有文件
            for fileName in fileNames:
                yield os.path.join(path, fileName)

    @classmethod
    def get_dir_all_dir(cls, s_path):
        """
        获取目录下的最深子目录
        # 这里注意topdown参数。
        # topdown决定遍历的顺序，
        # 如果topdown为True，则先列举top下的目录，然后是目录的目录，依次类推；
        # 反之，则先递归列举出最深层的子目录，然后是其兄弟目录，然后父目录。
        # 我们需要先修改深层的子目录
        :param path:  给定一个路径 如 C:/Users/XD/Pictures/所有视频/
        :return:
        """
        # 遍历子目录
        assert cls.is_dir(s_path), NotADirectoryError(s_path + " not is a dir please check")
        for path, dirNames, fileNames in os.walk(s_path, topdown=False):
            # 获取当前目录的所有文件
            for one_dir in dirNames:
                f_path = os.path.join(path, one_dir)
                for path1, dirNames1, fileNames1 in os.walk(f_path):
                    if len(dirNames1) == 0:
                        yield f_path
                    # break 原因是当一个目录有子目录时 会循环子目录，所以一次判断就可以了
                    break

    @classmethod
    def is_dir_exists(cls, pathdir):
        """
        目录是否存在
        :param sPth:
        :return:
        """
        return os.path.exists(pathdir)

    @classmethod
    def create_dir(cls, pathdir):
        """
        创建目录 该方法可以创建多级目录
        os.mkdir(pathdir)是创建一级目录 该目录的上级目录必须存在
        :param pathdir:
        :return:
        """
        if not cls.is_dir_exists(pathdir):
            os.makedirs(pathdir)

    @classmethod
    def get_upper_dir(cls, curPath: str, num: int) -> str:
        """
        获取上几层的目录，如果包含文件名 -1 代表着这个文件的目录
        :param curPath:
        :param num:
        :return:
        """
        # 如果不是个整数
        if not isinstance(num, int) or num > 0:
            warnings.warn("this not int or num > 0 , The path is not processed, return curPath")
            return curPath
        pathlist = curPath.split(os.sep)
        if abs(num) > (len(pathlist) - 1):
            warnings.warn("this path length < num ,will return root dir ")
            num = (len(pathlist) - 1) * (-1)
        pathlist = pathlist[:num]
        TopPath = os.sep.join(pathlist)
        return TopPath

    @classmethod
    def get_file_dir_absolute(cls, file):
        """
        请传入 __file__ 作为参数
        获取一个文件的绝对路径
        :param __file__:
        :return:
        """
        curPath = os.path.dirname(os.path.abspath(file))
        return curPath

    @classmethod
    def is_dir(cls, spath):
        if os.path.isdir(spath):
            return True
        return False

    @classmethod
    def get_dir_size(cls, dirpath):
        """
        1eb = 1024pb
        1pb = 1024tb
        1tb = 1024gb
        1gb = 1024mb
        1mb = 1024kb
        1kb = 1024b
        上面的b是Byte
        1Byte = 8bit
        :param dirpath:
        :return: 这里返回的是Byte大小
        """
        size = 0
        for filepath in cls.get_dir_all_files(dirpath):
            size += sum(BaseFile.get_file_size(filepath))
        return size

    @classmethod
    def copy_file_to_dir(cls, filePath, tarDirPath):
        """

        :param filePath:  文件路径
        :param tarDirPath:  目录或文件路径
        :return:
        """
        assert BaseFile.is_file_exists(filePath), FileNotFoundError("需要copy的文件不存在")
        assert BaseFile.is_file(filePath), FileNotFoundError("需要copy的不是一个文件")
        cls.create_dir(tarDirPath)
        shutil.copy(filePath, tarDirPath)

    @classmethod
    def copy_dir_to_dir(cls, oldDir, newDir, moudle=0):
        """
        olddir和newdir都只能是目录，且newdir必须不存在
        :param oldDir:
        :param newDir:
        :return:
        """
        assert cls.is_dir(oldDir), IsADirectoryError(oldDir + "目录不存在")
        if moudle == 0:
            # 该模式下新目录必须不存在
            assert not cls.is_dir(newDir), IsADirectoryError(newDir + "目录存在，不能使用该模式,推荐使用模式2")
            shutil.copytree(oldDir, newDir)
        elif moudle == 1:
            # 该模式下如果新目录存在先删除新目录
            if cls.is_dir(newDir):
                cls.delete_dir(newDir)
            shutil.copytree(oldDir, newDir)
        elif moudle == 3:
            # 该模式下通过替换进行copy
            pass
        elif moudle == 4:
            # 该模式会跳过已存在的文件 只将新文件放入其中
            pass

    @classmethod
    def delete_dir(cls, dirpath):
        """
         os.rmdir(dirpath) 只能删除空目录
        os.removedirs(path)  递归的删除目录
        :param dirpath:
        :return:
        """
        shutil.rmtree(dirpath)

    @classmethod
    def replace_dir_special_string(cls, strings):
        """
        windows 目录非法字符
        :param strings:
        :return:
        """
        strings1 = strings.replace("/", "").replace("\\", "") \
            .replace(":", "").replace("*", "").replace("\"", "") \
            .replace("<", "").replace(">", "").replace("|", "") \
            .replace("?", "")
        return strings1

    @classmethod
    def remove_file_suf(cls, dirpath, suf):
        for file in cls.get_dir_all_files(dirpath):
            if file.endswith(suf):
                BaseFile.remove_file(file)

    @classmethod
    def is_null_dir(cls, dirpath):
        """
        是否为空目录
        :param dirpath:
        :return:
        """
        if not os.listdir(dirpath):
            return True
        return False

    @classmethod
    def get_dir_file_num(cls, dirpath):
        return len([name for name in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, name))])

    @classmethod
    def get_dir_all_file_num(cls, dirpath, ext=None):
        """
        获取目录下所有文件个数，包含目录下目录的个数
        :return:
        """
        count = 0
        for path in cls.get_dir_all_files(dirpath):
            if BaseFile.is_file(path):
                if ext is not None:
                    if path.endswith(ext):
                        count += 1
            elif cls.is_dir(path):
                count = count + cls.get_dir_all_file_num(path, ext)
        return count

    @classmethod
    def get_dir_all_file_size(cls, dirpath, ext=None):
        """
        获取目录下所有文件的总大小
        :return:
        """
        count = 0
        for path in cls.get_dir_all_files(dirpath):
            if BaseFile.is_file(path):
                if ext is not None:
                    if path.endswith(ext):
                        count = count + BaseFile.get_file_size(path)
            elif cls.is_dir(path):
                count = count + cls.get_dir_all_file_num(path, ext)
        return count

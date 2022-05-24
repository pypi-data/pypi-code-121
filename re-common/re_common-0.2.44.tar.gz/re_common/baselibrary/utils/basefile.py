import _io
import linecache
import os
import platform
import random
import re
import shutil
import time
import traceback

from .core.bottomutils import __os_sep__


class BaseFile(_io.TextIOWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def seek(self, offset: int, whence: int = 0) -> int:
        """
        :param offset: 开始偏移量，也就是代表需要移动偏移的字节数。
        :param whence: 给offset参数一个定义，表示要从哪个位置开始偏移；0
        代表从文件开头开始算起，1代表从当前位置开始算起，2代表从文件末尾算起
        :return: 返回的游标的位置
        """
        super().seek(offset, whence=whence)
        return super().tell()

    def truncate(self, size: int = None) -> int:
        """
        Python 文件 truncate() 方法用于截断文件并返回截断的字节长度。

        指定长度的话，就从文件的开头开始截断指定长度，其余内容删除；
        不指定长度的话，就从文件开头开始截断到当前位置，其余内容删除。
        文件中的数据也会删除
        :param size:
        :return:
        """
        super().truncate(size)
        return super().tell()

    @classmethod
    def read_line(cls, file_path, encoding="utf-8"):
        """
        按行读取文件
        会一次性读取文件生成list  不适合大文件
        :param file_path:
        :param encoding:
        :return:
        """
        try:
            with open(file_path, "r", encoding=encoding) as f:
                for line in f.readlines():
                    yield line.strip()
        except:
            print(traceback.format_exc())

    @classmethod
    def read_file_r_mode_yield(cls, filePath, encoding="utf-8"):
        """
        rb 模式比r 模式更快 但要通过编码格式转换才能使用 对于转移文件使用会更快
        :param filePath:
        :return:
        """
        with open(filePath, "r", encoding=encoding) as f:
            for fLine in f:
                yield fLine.strip()

    @classmethod
    def read_file_rb_mode_yield(cls, filePath):
        """
        rb 方式读取文件
        for line in f文件对象f视为一个迭代器，会自动的采用缓冲IO和内存管理，所以你不必担心大文件
        参数为"rb"时的效率是"r"的6倍 建议rb
        这里说下转str的方法 str(line, encoding='utf-8')
        :param filePath:
        :return: type bytes
        """
        with open(filePath, "rb") as f:
            for fLine in f:
                yield fLine

    @classmethod
    def read_file_rb_block(cls, filePath, BLOCK_SIZE=1024):
        """
        按块读取文件
        :param filePath:
        :param BLOCK_SIZE:
        :return:
        """
        with open(filePath, 'rb') as f:
            while True:
                block = f.read(BLOCK_SIZE)
                if block:
                    yield block
                else:
                    return

    @classmethod
    def read_file_rb(cls, filePath: str) -> bytes:
        assert cls.is_file_exists(filePath), FileNotFoundError("文件不存在%s" % filePath)
        with open(filePath, mode='rb') as f:
            return f.read()

    @classmethod
    def bytes_takeout_utf8bom(cls, content: bytes):
        if content.startswith(b'\xef\xbb\xbf'):  # 去掉 utf8 bom 头
            return content[3:]
        return content

    @classmethod
    def readfile_rb_takeout_utf8bom(cls, cfgFile: str) -> bytes:
        content = cls.read_file_rb(cfgFile)
        content = cls.bytes_takeout_utf8bom(content)
        return content

    @classmethod
    def get_new_path(cls, path, *paths):
        """
        通过当前目录组合新的目录
        :return:
        """
        if platform.system() == "Windows":
            if (re.match("^[A-Za-z]:$", path)):
                path = path + "\\"
        path = os.path.join(path, *paths)
        return path

    @classmethod
    def check_create_dir(cls, path):
        """
        检查和创建目录
        :param path:
        :return:
        """
        if os.path.exists(path):
            return True
        else:
            os.makedirs(path)
            return False

    @classmethod
    def single_write_file(cls, files, value, encoding="utf-8"):
        """
        单次将内容写入文件
        写入值到文件 每次写入会覆盖原来的文件  文件不存在会自动创建
        :param value:
        :param files:
        :return:
        """
        with open(files, 'w', encoding=encoding) as f:
            f.write(value)

    @classmethod
    def single_write_file_lines(cls, files, value_list, encoding="utf-8"):
        """
        单次将内容写入文件
        写入值到文件 每次写入会覆盖原来的文件  文件不存在会自动创建
        :param value:
        :param files:
        :return:
        """
        with open(files, 'w', encoding=encoding) as f:
            f.writelines(value_list)

    @classmethod
    def single_write_wb_file(cls, files, value):
        """
        单次将内容写入文件
        写入值到文件 每次写入会覆盖原来的文件  文件不存在会自动创建
        :param value:
        :param files:
        :return:
        """
        with open(files, 'wb') as f:
            f.write(value)

    @classmethod
    def single_write_ab_file(cls, files, value):
        """
        单次将内容写入文件
        写入值到文件 每次写入会追加原来的文件  文件不存在会自动创建
        :param value:
        :param files:
        :return:
        """
        with open(files, 'ab') as f:
            f.write(value)

    @classmethod
    def get_file_absolute(cls, file):
        """
        请传入 __file__ 作为参数
        获取一个文件的绝对路径
        :param __file__:
        :return:
        """
        return os.path.abspath(file)

    @classmethod
    def single_read_file(cls, filePath, encoding="utf-8", num=-1):
        """
        读取文件中的所有值
        :param filePath:
        :param encoding:
        :param num  读取指定长度 可以用于解决无换行大文件问题 默认-1读取全部
        :return:
        """
        with open(filePath, encoding=encoding) as f:
            return f.read(num)

    @classmethod
    def single_read_rb_file(cls, filePath):
        """
        读取文件中的所有值
        :param filePath:
        :param encoding:
        :return:
        """
        with open(filePath, "rb") as f:
            return f.read()

    @classmethod
    def get_file_row(cls, filePath, linenum):
        return linecache.getline(filePath, linenum)

    @classmethod
    def get_file_line_num(cls, filePath, encoding="utf-8"):
        """
        获取文件行数
        :param filePath:
        :return:
        """
        count = 0
        for index, line in enumerate(open(filePath, 'r', encoding=encoding)):
            count += 1
        return count

    @classmethod
    def single_add_file(cls, filePath, value, encoding="utf-8"):
        """
        追加文件中的所有值
        文件不存在创建
        :param filePath:
        :param encoding:
        :return:
        """
        with open(file=filePath, mode="a", encoding=encoding) as f:
            f.write(value)

    @classmethod
    def add_file_ab_mode(cls, filePath, value):
        """
        追加文件中的所有值
        :param filePath:
        :param encoding:
        :return:
        """
        with open(file=filePath, mode="ab") as f:
            f.write(value)

    @classmethod
    def copy_file_to_file(cls, soufilePath, desfilepath):
        """
        shutil.copy 实现了copy文件
        :param soufilePath: 必须是一个文件
        :param desfilepath: 可以是一个文件 或者目录 如果是文件且文件名不同 可以达到重命名的效果
        当我们想将文件copy成一个无后缀文件 且当前目录已经有一个同名文件夹时 会将文件copy到文件夹中
        而不是一个无后缀文件中 这里要注意在大量文件和文件夹中使用时产生的歧义，且不能定义一个文件与文件夹
        重名
        :return:
        """
        assert cls.is_file(soufilePath), FileNotFoundError(soufilePath + "这不是一个文件的路径")
        # 不存在进行创建目录
        if not os.path.exists(desfilepath):
            # 判断上级目录是否存在
            if not os.path.exists(os.path.split(desfilepath)[0]):
                os.makedirs(os.path.split(desfilepath)[0])
        # copy文件
        shutil.copyfile(soufilePath, desfilepath)
        # 判断copy后的文件是否存在
        if os.path.isfile(desfilepath):
            return True
        else:
            raise FileExistsError(desfilepath + "不存在，可能被copy到" + desfilepath + "目录中")

    @classmethod
    def get_image_filename_time(cls, filename):
        # 这是从文件名中获取时间  主要用于手机图片的命名格式有效
        li = filename.split(__os_sep__)
        if li[-1].find(__os_sep__) != -1:
            return ''
        if li[-1].find(os.extsep) != -1:
            li2 = li[-1].split(os.extsep)
            li3 = li2[-2].split("_")
            if len(li3) == 1:
                return li3[0]
            return li3[-2] + li3[-1]
        return ''

    @classmethod
    def get_time(cls, filename):
        """
        获取文件时间，这个是获取文件的属性，不利于获取创造时间 因为每一次更改时间都会更新
        :param filename:
        :return:
        """
        ModifiedTime = time.localtime(os.stat(filename).st_mtime)  # 文件访问时间
        y = time.strftime('%Y', ModifiedTime)
        m = time.strftime('%m', ModifiedTime)
        d = time.strftime('%d', ModifiedTime)
        H = time.strftime('%H', ModifiedTime)
        M = time.strftime('%M', ModifiedTime)
        import datetime
        d2 = datetime.datetime(int(y), int(m), int(d), int(H), int(M))
        return d2

    @classmethod
    def secure_filename(cls, filename):
        r"""Pass it a filename and it will return a secure version of it.  This
        filename can then safely be stored on a regular file system and passed
        to :func:`os.path.join`.  The filename returned is an ASCII only string
        for maximum portability.

        On windows systems the function also makes sure that the file is not
        named after one of the special device files.

        经我改变 支持中文

        >>> secure_filename("My cool movie.mov")
        'My_cool_movie.mov'
        >>> secure_filename("../../../etc/passwd")
        'etc_passwd'
        >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
        'i_contain_cool_umlauts.txt'

        The function might return an empty filename.  It's your responsibility
        to ensure that the filename is unique and that you generate random
        filename if the function returned an empty one.

        .. versionadded:: 0.5

        :param filename: the filename to secure
        """
        if isinstance(filename, text_type):
            # 此模块提供对Unicode字符数据库的访问，该字符数据库为所有Unicode字符定义字符属性。该数据库中的数据基于UnicodeData.txt
            # 可从ftp://ftp.unicode.org/公开获得的文件版本5.2.0 。
            from unicodedata import normalize
            # ignore参数会忽略无法编码的字符
            # normalize 为标准化底层编码 http://python3-cookbook.readthedocs.io/zh_CN/latest/c02/p09_normalize_unicode_text_to_regexp.html
            filename = normalize('NFKD', filename).encode('utf-8')
            if not PY2:
                filename = filename.decode('utf-8')
        for sep in os.path.sep, os.path.altsep:
            if sep:
                # 替换用后面的替换前面的
                filename = filename.replace(sep, ' ')
        filename = str(re.sub(':', '', '_'.join(
            filename.split()))).strip('._')

        # on nt a couple of special files are present in each folder.  We
        # have to ensure that the target file is not such a filename.  In
        # this case we prepend an underline
        if os.name == 'nt' and filename and \
                filename.split('.')[0].upper() in _windows_device_files:
            filename = '_' + filename

        return filename

    @classmethod
    def get_file_ext_name(cls, filename, double_ext=False):
        """
        获取文件后缀
        os.extsep = "."
        :param filename: 传入文件名或者带路径的文件
        :param double_ext:
        :return:
        """
        li = filename.split(os.extsep)  # 以.分割
        if len(li) <= 1:  # 如果分割后只有一个  那么这没有文件后缀
            return ''
        else:
            if li[-1].find(__os_sep__) != -1:  # 如果在最后一个中发现分割符 也没有后缀
                return ''
        if double_ext:
            if len(li) > 2:  # 有可能后缀有多个组成 这里我们最多返回两个字符串以点链接形成的后缀
                if li[-2].find(__os_sep__) == -1:
                    return '%s.%s' % (li[-2], li[-1])
        return li[-1]

    @classmethod
    def get_filename_not_extsep(cls, filename, end=None):
        """
        获取文件名  去除后缀和路径
        :param filename:
        :return:
        """
        filename = cls.get_file_name(filename)
        if end is None:
            return os.extsep.join(filename.split(os.extsep)[:-1])
        else:
            if filename.endswith(end):
                return filename[:len(filename) - len(end) - 1]
            return os.extsep.join(filename.split(os.extsep)[:-1])

    @classmethod
    def get_file_name(cls, filename):
        """
        得到文件名  去掉路径
        :param filename:
        :return:
        """
        # assert cls.is_file(filename), FileNotFoundError("传入的文件路径不正确")
        return os.path.split(filename)[-1]
        # 旧的方式 废弃
        # return filename.split(__os_sep__)[-1]

    @classmethod
    def new_title(cls, title):
        """
        替换掉标题里的特殊符号 方便保存
        :param title:
        :return:
        """
        err_str = r"[\/\\\:\*\?\"\<\>\|]"
        new_title = re.sub(err_str, "_", title)
        return new_title

    @classmethod
    def is_file_exists(cls, pathdir):
        """
        目录是否存在
        :param sPth:
        :return:
        """
        if os.path.exists(pathdir) and cls.is_file(pathdir):
            return True
        else:
            return False

    @classmethod
    def get_file_size(cls, filePath):
        assert os.path.isfile(filePath), FileNotFoundError("你给出的路径的文件不存在")
        return os.path.getsize(filePath)

    @classmethod
    def is_file(cls, spath):
        """
        判断传入的路径是否是一个文件
        :param spath:
        :return:
        """
        if os.path.isfile(spath):
            return True
        return False

    @classmethod
    def remove_file(cls, filepath):
        """
        删除文件
        :param filepath:
        :return:
        """
        os.remove(filepath)

    @classmethod
    def rename_file(cls, filepath, sourpath):
        os.rename(filepath, sourpath)

    @classmethod
    def get_create_time(cls, filepath):
        # 创建时间
        return os.path.getctime(filepath)

    @classmethod
    def get_update_time(cls, filepath):
        # 修改时间
        return os.path.getmtime(filepath)

    @classmethod
    def change_file(cls, filepath, sign='_', ending='big_json', size=2 * 1024 * 1024 * 1024):
        """
        :param filepath: 传入验证文件
        :param size: 文件大小限制(字节比较)(默认为2GB)
        :param sign: 文件切换后缀的标志 默认为"_"
        :param ending: 后缀名
        :return: 一个新的文件名
        注意 首次传入的文件名不能包含sign标志位
        """
        from re_common.baselibrary.utils.basedir import BaseDir
        uppath = BaseDir.get_upper_dir(filepath, -1)
        if not cls.is_file_exists(filepath):
            return filepath
        else:
            if cls.get_file_size(filepath) >= size:
                import random
                # 无后缀文件名
                filename = cls.get_filename_not_extsep(filepath, end=ending)
                if sign in filename:
                    path_list = filename.split(sign)
                    if path_list[-1].isdigit() and len(path_list[-1]) == 5:
                        # 原生文件名无数字干扰
                        filename = filename[:-len(path_list[-1]) - 1]
                filename = filename + sign + repr(random.randrange(10000, 99999)) + "." + ending

                path = cls.get_new_path(uppath, filename)
                if cls.is_file_exists(path):
                    return cls.change_file(path, sign=sign, ending=ending, size=size)
                return path
            else:
                return filepath

    @classmethod
    def get_new_filename(cls, filepath, sign='_', ending='big_json.gz'):
        # 如果传入的文件名在路径下不存在直接使用该文件名
        if not cls.is_file_exists(filepath):
            return filepath
        else:
            from re_common.baselibrary.utils.basedir import BaseDir
            # 获取路径
            uppath = BaseDir.get_upper_dir(filepath, -1)
            # 获取文件名但只会去除默认的一个后缀
            if sign in cls.get_filename_not_extsep(filepath):
                path_list = cls.get_file_name(filepath).split(sign)
                filename = path_list[0] + sign + repr(random.randrange(11111, 99999)) + "." + ending
            else:
                filename = cls.get_file_name(filepath)
                filename = filename.replace(("." + cls.get_file_ext_name(filepath)),
                                            (sign + repr(random.randrange(11111, 99999)) + "." + ending))
            path = cls.get_new_path(uppath, filename)
            if cls.is_file_exists(path):
                return cls.change_file(path, sign=sign, ending=ending)
            return path

    @classmethod
    def file_is_update_days(cls, filepath, days=3):
        """
        判断文件是否在3天内 有更新
        True 3天内有更新 否则更新在3天以前
        :param days:
        :return:
        """
        if BaseFile.is_file_exists(filepath):
            ctime = os.path.getctime(filepath)  # 创建时间
            mtime = os.path.getmtime(filepath)  # 修改时间
            if ((time.time() - ctime) / 3600 / 24 < days) or ((time.time() - mtime) / 3600 / 24 < days):
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def copy_file_to_dir(cls, soufilePath, desfilepath):
        """
        copy 文件到目录
        :param file:
        :param destdir: 目标目录
        :return:
        """
        assert cls.is_file(soufilePath), FileNotFoundError(soufilePath + "这不是一个文件的路径")
        # 不存在进行创建目录
        if not os.path.exists(desfilepath):
            # 判断上级目录是否存在
            if not os.path.exists(os.path.split(desfilepath)[0]):
                os.makedirs(os.path.split(desfilepath)[0])
        # copy文件
        shutil.copy(soufilePath, desfilepath)

    @classmethod
    def is_open(cls,file_name):
        """
        文件是否被其他进程打开
        :param file_name:
        :return:
        """
        if "Windows" == platform.system():
            import win32file
            try:
                vHandle = win32file.CreateFile(file_name, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING,
                                               win32file.FILE_ATTRIBUTE_NORMAL, None)
                return int(vHandle) == win32file.INVALID_HANDLE_VALUE
            except:
                if "另一个程序正在使用此文件，进程无法访问。" in traceback.format_exc():
                    return True
                else:
                    return False
            finally:
                try:
                    win32file.CloseHandle(vHandle)
                except:
                    pass
        else:
            raise Exception("不是windows系统，请不要调用该函数判断文件是否被打开")
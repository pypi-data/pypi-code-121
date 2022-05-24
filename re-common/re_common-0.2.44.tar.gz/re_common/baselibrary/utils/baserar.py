import patoolib
import rarfile as rarfile

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.baseodbc import BaseODBC


class BaseRAR(object):

    @classmethod
    def get_rar_file(cls, filepath):
        azip = rarfile.RarFile(filepath)
        return azip

    @classmethod
    def get_rar_namelist(cls, rar_obj):
        result_list = []
        for f in rar_obj.infolist():
            result_list.append(f.filename)

        return result_list

    @classmethod
    def get_file_obj(cls, rar_obj):
        """
        返回的是一个可迭代对象
        :param rar_obj:
        :return:
        """
        return rar_obj.infolist()

    @classmethod
    def extractall(cls, rarobj, **kwargs):
        """
        解压所有文件
        rarfile.RarCannotExec: Cannot find working tool
        C:\Program Files (x86)\WinRAR 加入环境变量 重启pycharm
        但还是有问题
        rarfile.BadRarFile: Failed the read enough data: req=1048576 got=0
        pip install unrar 也无效
        :return:
        """
        return rarobj.extractall(**kwargs)

    @classmethod
    def extractall_patoolib(cls, file_path, outdir):
        patoolib.extract_archive(file_path, outdir=outdir)


# file_path = r'C:\Users\xuzhu\Desktop\VIPPatents_20210618To20210622.rar'
# rarobj = BaseRAR.get_rar_file(file_path)
# fileobj = BaseRAR.extractall(rarobj, path=r'C:\Users\xuzhu\Desktop')
#
# for file in BaseDir.get_dir_all_files(r"\\192.168.31.184\caiji\cnipr黄斌"):
#     if file.find("VIPPatents_2021") > -1:
#         print(file)
#         BaseRAR.extractall_patoolib(file, outdir=r'\\192.168.31.171\caiji\patent')

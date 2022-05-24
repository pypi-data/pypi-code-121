"""
重命名目录下的文件
"""
from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile


def get_next_suffix(num):
    num = num + 1
    return "_" + str(num).zfill(4)


def rename_db3(dirpath, rename, start=0):
    """
    重命名db3　文件　以后缀_001 或者　_000 开始
    :param rename:
    :param start: 1 代表_001　0代表_000
    :return:
    """
    """
    
    :param dirpath: 
    :param rename: 
    :param start: 
    :return: 
    """

    for file in BaseDir.get_dir_all_files(dirpath):
        if file.endswith(".db3"):
            BaseDir.get_upper_dir(file, -1)
            renamepath = BaseFile.get_new_path(dirpath, rename + get_next_suffix(start) + ".db3")
            BaseFile.rename_file(file, renamepath)
            start = start + 1


rename_db3(r"\\192.168.31.65\d$\zt_data_db3\zt_normal_grx\zt_cnki_qk_20200323", "zt_cnki_qk_20200323")
rename_db3(r"\\192.168.31.65\d$\zt_data_db3\zt_normal_grx\zt_wf_qk_20200323", "zt_wf_qk_20200323")

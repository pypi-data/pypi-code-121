###########################################
# 同项目调用基础包
import os
import shutil
import sys

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-4]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)
############################################

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile

source_dir = r"\\192.168.31.169\down_data\cnki_hy_quanwen\20200530\vcode"
dst_dir = r"F:\fun2\jpg"
BaseDir.create_dir(dst_dir)
log_path = r"F:\fun2\log.txt"
count = 0
for file in BaseDir.get_dir_all_files(source_dir):
    print(file)
    count = count + 1
    try:
        filename = BaseFile.get_file_name(file)
        filepath = BaseDir.get_file_dir_absolute(file)
        new_sub_dir = filepath.replace(source_dir, "")
        new_dir = dst_dir + new_sub_dir
        BaseDir.create_dir(new_dir)
        new_path = new_dir + "\\" + filename
        shutil.copyfile(file, new_path)
    except:
        print("err:" + file)
        BaseFile.single_add_file(log_path, file)
    # if count % 10000 == 1:
    #     print(count)
    print(count)

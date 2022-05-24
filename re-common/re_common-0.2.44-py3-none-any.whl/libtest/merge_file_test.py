###########################################
# 同项目调用基础包
import os
import sys

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-3]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)
############################################
from re_common.baselibrary.tools.merge_file import MergeFile

if __name__ == '__main__':
    old_path = r'E:\work\pnasjournal\big_json\20200116'
    new_path = r'E:\work\pnasjournal\big_json\new'
    a = MergeFile()
    # a.line_all_2_one(old_path,new_path)
    a.block_all_2_one(old_path, new_path, dst_size=1024 * 1024 * 200, block_size=200 * 1024 * 1024)

# 同项目调用基础包
import os
import sys

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-5]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)

#################

from re_common.baselibrary.utils.basefile import BaseFile
"""
通过rawid 和batch 找出一组中batch比另一组大的数据
"""


dicts1 = {}
dicts2 = {}

for line in BaseFile.read_file_r_mode_yield("./files/part-1"):
    lists = line.split(";")
    dicts1[lists[0]] = lists[1]

count = 0
for line in BaseFile.read_file_r_mode_yield("./files/part-2"):
    lists = line.split(";")
    if lists[0] in dicts1.keys():
        if not lists[1] == dicts1[lists[0]]:
            BaseFile.single_add_file("./test.txt", line + "\n")

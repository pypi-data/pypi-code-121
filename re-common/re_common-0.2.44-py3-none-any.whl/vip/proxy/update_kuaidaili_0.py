import json

###########################################
# 同项目调用基础包
import os
import sys
import time

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-4]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)
############################################

from re_common.baselibrary.utils.baserequest import BaseRequest
from re_common.facade.mysqlfacade import MysqlUtiles
from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile
from re_common.facade.lazy_import import get_streamlogger


class Kproxy(object):
    def __init__(self):
        self.cur_path = BaseDir.get_file_dir_absolute(__file__)
        self.configfile = BaseFile.get_new_path(self.cur_path, "db.ini")
        self.logger = get_streamlogger()
        self.mysqlutils = MysqlUtiles(self.configfile, "dbkuaidaili", self.logger)
        self.starttime = time.time()
        self.starttime_val = time.time()

    def run(self):
        sql = "update `kuaidailiproxy` set val_stat=1 WHERE stat=1"
        self.mysqlutils.ExeSqlToDB(sql)


if __name__ == "__main__":
    k = Kproxy()
    while True:
        k.run()
        time.sleep(60*2)

import json

###########################################
# 同项目调用基础包
import os
import sys
import time
import traceback

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
        self.url = "https://dps.kdlapi.com/api/getdps/?orderid=990171566857288&num=15&pt=1&format=json&sep=1"
        self.bsrequest = BaseRequest()
        self.starttime = time.time()
        self.starttime_val = time.time()

    def get_proxy(self):
        self.starttime = time.time()
        BoolResult, errString, r = self.bsrequest.base_request(self.url,
                                                               timeout=30
                                                               )
        if BoolResult:
            dicts = json.loads(r.text)
            for proxy in dicts["data"]["proxy_list"]:
                sql = "insert into kuaidailiproxy (proxy) values ('%s') on DUPLICATE key update stat=1" % proxy
                self.mysqlutils.ExeSqlToDB(sql)
        else:
            self.logger.error("获取失败")

    def val(self, proxy):
        self.starttime_val = time.time()
        url = f"https://dps.kdlapi.com/api/getdpsvalidtime?orderid=990171566857288&signature=wm4vq53pwrat1vye458elwyxyh9awzqj&proxy={proxy}"
        BoolResult, errString, r = self.bsrequest.base_request(url,
                                                               timeout=30
                                                               )
        if BoolResult:
            dicts = json.loads(r.text)
            if dicts["data"][proxy] > 0:
                sql = "update kuaidailiproxy set val_stat=0 where proxy='%s'" % proxy
                self.mysqlutils.ExeSqlToDB(sql)
            else:
                sql = "update kuaidailiproxy set val_stat=0,stat=0 where proxy='%s'" % proxy
                self.mysqlutils.ExeSqlToDB(sql)
        else:
            self.logger.error("获取失败")

    def val_all(self):
        self.starttime_val = time.time()
        sql = "select proxy from kuaidailiproxy where stat=1"
        bools, rows = self.mysqlutils.SelectFromDB(sql)
        for row in rows:
            try:
                self.val(row[0])
            except:
                traceback.print_exc()

    def run(self):
        self.get_proxy()
        while True:
            if int(time.time() - self.starttime) > 20:
                self.get_proxy()
            if int(time.time() - self.starttime_val) > 30:
                self.val_all()
            time.sleep(5)


if __name__ == "__main__":
    Kproxy().run()

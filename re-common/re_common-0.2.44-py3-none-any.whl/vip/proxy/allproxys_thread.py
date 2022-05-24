import json
###########################################
# 同项目调用基础包
import os
import sys
import time

import requests

from re_common.baselibrary.mthread.MThreadingRun import MThreadingRun
from re_common.baselibrary.mthread.mythreading import ThreadInfo, ThreadVal, ThreadPoolManger

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-4]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)
############################################

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile
from re_common.baselibrary.utils.baserequest import BaseRequest
from re_common.facade.lazy_import import get_streamlogger
from re_common.facade.mysqlfacade import MysqlUtiles


class Kproxy(object):
    def __init__(self):
        self.cur_path = BaseDir.get_file_dir_absolute(__file__)
        self.configfile = BaseFile.get_new_path(self.cur_path, "db.ini")
        self.logger = get_streamlogger()
        self.mysqlutils = MysqlUtiles(self.configfile, "allproxy", self.logger)
        self.bsrequest = BaseRequest()
        self.starttime = time.time()
        self.starttime_val = time.time()

    def get_taiyang_proxy(self, num=6):
        """
        获取太阳代理 每分钟3个
        :param num:
        :return:
        """
        self.starttime = time.time()
        url = "http://http.tiqu.qingjuhe.cn/getip?num={}&type=2&pack=56912&port=1&ts=1&lb=1&pb=45&regions=".format(num)
        BoolResult, errString, r = self.bsrequest.base_request(url,
                                                               timeout=30
                                                               )
        if BoolResult:
            dicts = json.loads(r.text)
            for item in dicts["data"]:
                proxy = item["ip"] + ":" + item["port"]
                sources = "taiyang"
                expire_time = item["expire_time"]
                sql = "insert into proxyall_v1 (proxy,sources,expire_time) values ('%s','%s','%s') on DUPLICATE key update stat=1,expire_time='%s'" % (
                    proxy, sources, expire_time, expire_time)
                self.mysqlutils.ExeSqlToDB(sql)
        else:
            self.logger.error("获取失败")

    def val(self, proxy, sources,threadval):
        # 请求地址
        targetUrl = "https://www.baidu.com"
        proxies = {
            "http": "http://%s" % proxy,
            "https": "http://%s" % proxy
        }
        resp = requests.get(targetUrl, proxies=proxies, timeout=5)
        if resp.status_code == 200:
            print(resp.status_code)
            sql = "update proxyall_v1 set stat=1 where proxy='%s' and sources='%s';" % (proxy, sources)
            threadval.get_result_queue().put(sql)
            return True
        else:
            sql = "update proxyall_v1 set stat=0 where proxy='%s' and sources='%s';" % (proxy, sources)
            # self.mysqlutils.ExeSqlToDB(sql)
            threadval.get_result_queue().put(sql)
            return False

    def val_all(self):
        self.starttime_val = time.time()
        sql = "select proxy,sources from proxyall_v1 where stat=1 ORDER BY `update_time`"
        bools, rows = self.mysqlutils.SelectFromDB(sql)
        for row in rows:
            try:
                self.val(row[0], row[1])
            except:
                sql = "update proxyall_v1 set stat=0 where proxy='%s' and sources='%s';" % (row[0], row[1])
                self.mysqlutils.ExeSqlToDB(sql)

    def run(self):
        while True:
            start_time = time.time()
            self.get_taiyang_proxy()
            self.val_all()
            use_time = int(time.time() - start_time)
            sleep_time = 100 - use_time
            print("time sleep {}".format(str(sleep_time)))
            if sleep_time >= 3:
                time.sleep(sleep_time)


class DetailThreadRun(MThreadingRun):
    def __init__(self, num):
        self.down = Kproxy()
        super(DetailThreadRun, self).__init__(num)

    @ThreadPoolManger.thread_lock
    def getTask(self, *args, **kwargs):
        sql = "select proxy,sources from proxyall_v1 where stat=0 ORDER BY `expire_time` DESC limit 1000"
        bools, rows = self.down.mysqlutils.SelectFromDB(sql)
        return rows

    @ThreadPoolManger.thread_lock
    def getTask2(self, *args, **kwargs):
        sql = "select proxy,sources from proxyall_v1 where stat=1 ORDER BY `expire_time` DESC limit 1000"
        bools, rows = self.down.mysqlutils.SelectFromDB(sql)
        return rows

    def setTask(self, results=None, *args, **kwargs):
        if not results:
            return self.BREAK
        for row in results:
            self.add_job(self.func, row[0], row[1])
        rows = self.getTask2()
        for row in rows:
            self.add_job(self.func, row[0], row[1])
        time.sleep(60*2)
        return self.BREAK

    @ThreadPoolManger.thread_lock
    def dealresult(self, *args, **kwargs):
        # for sql in self.results:
        #     self.down.mysqlutils.ExeSqlToDB(sql)
        self.down.mysqlutils.ExeSqlListToDB(self.results)

    def setProxy(self, proxysList=None):
        time.sleep(300)

    def is_break(self):
        return False

    def thread_pool_hook(self, threadinfo: ThreadInfo):
        # 设置代理线程不重启，默认会重启
        return {}

    def fun(self, threadval: ThreadVal, *args, **kwargs):
        proxy,sources = args[0],args[1]
        try:
            self.down.val(proxy, sources, threadval)
        except:
            sql = "update proxyall_v1 set stat=0 where proxy='%s' and sources='%s';" % (proxy, sources)
            # self.mysqlutils.ExeSqlToDB(sql)
            threadval.get_result_queue().put(sql)


if __name__ == '__main__':
    down = DetailThreadRun(30)
    down.run()

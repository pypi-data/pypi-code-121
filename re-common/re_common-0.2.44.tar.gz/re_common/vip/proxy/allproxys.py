import json
###########################################
# 同项目调用基础包
import os
import sys
import time

import requests

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
from re_common.baselibrary.utils.basetime import BaseTime


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
        #  url = "http://http.tiqu.qingjuhe.cn/getip?num={}&type=2&pack=59105&port=1&ts=1&lb=1&pb=45&regions=".format(num)
        url = "http://http.tiqu.alibabaapi.com/getip?num={}&type=2&pack=59105&port=1&ts=1&lb=1&pb=45&regions=".format(num)
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

    def get_taiyang_num(self):
        """
        获取太阳代理 每分钟3个
        :param num:
        :return:
        """
        url = "http://ty-http-d.hamir.net/index/index/get_my_package_balance?neek=521821&appkey=1fcba6de94f71561ba3007f4c24ca0b1&ac=59105"
        BoolResult, errString, r = self.bsrequest.base_request(url,
                                                               timeout=30
                                                               )
        if BoolResult:
            dicts = json.loads(r.text)
            return dicts["data"]["package_balance"]
        else:
            self.logger.error("获取失败")

    def val(self, proxy, sources):
        # 请求地址
        targetUrl = "https://www.baidu.com"
        proxies = {
            "http": "http://%s" % proxy,
            "https": "http://%s" % proxy
        }
        resp = requests.get(targetUrl, proxies=proxies, timeout=5)
        if resp.status_code == 200:
            print(resp.status_code)
            return True
        else:
            sql = "update proxyall_v1 set stat=0 where proxy='%s' and sources='%s';" % (proxy, sources)
            self.mysqlutils.ExeSqlToDB(sql)
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
        sleep_time = 0
        while True:
            num = 10
            if sleep_time < 0:
                print("time sleep {}".format(str(100 + sleep_time)))
                if 100 + sleep_time > 0:
                    time.sleep(100 + sleep_time)
                num = num + 10
            nowtime = BaseTime().get_beijin_date_strins(format="%H%M%S")
            print(nowtime)
            if "133700" <= nowtime <= "134700":
                num = Kproxy().get_taiyang_num()
            start_time = time.time()
            self.get_taiyang_proxy(num=num)
            self.val_all()
            use_time = int(time.time() - start_time)
            sleep_time = 100 - use_time
            print("time sleep {}".format(str(sleep_time)))
            if sleep_time >= 3:
                time.sleep(sleep_time)


if __name__ == "__main__":
    Kproxy().run()

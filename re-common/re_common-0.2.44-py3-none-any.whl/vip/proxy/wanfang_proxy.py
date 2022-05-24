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

from re_common.facade.loggerfacade import get_streamlogger
from re_common.baselibrary.mthread.MThreadingRun import MThreadingRun
from re_common.baselibrary.mthread.mythreading import ThreadPoolManger, ThreadInfo
from re_common.baselibrary.utils.baserequest import BaseRequest
from re_common.baselibrary.utils.core.requests_core import set_proxy
from re_common.baselibrary.utils.myredisclient import MyRedis
from re_common.facade.mysqlfacade import MysqlUtiles

from proxy_all import ProxyAll


class WanfangProxy(object):

    def __init__(self, config="./db.ini"):
        self.config = config
        self.logger = get_streamlogger()
        self.mysqlutils = MysqlUtiles(self.config, "dbwanfang", self.logger)
        self.Headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        self.baserequest = BaseRequest()

    def checking_proxy(self, proxy):
        url = "http://www.wanfangdata.com.cn/index.html"
        proxies = set_proxy(proxy)
        BoolResult, errString, r = self.baserequest.base_request(url,
                                                                 headers=self.Headers,
                                                                 proxies=proxies,
                                                                 marks=["container"],
                                                                 timeout=5)
        if BoolResult:
            return proxy
        return ""

    def get_mysql_proxy(self):
        sql = "SELECT proxy FROM `proxy_pool`"
        bools, rows = self.mysqlutils.SelectFromDB(sql)
        if not bools:
            return set()
        results = set()
        for row in rows:
            results.add(row[0])
        sql = "delete from proxy_pool"
        self.mysqlutils.ExeSqlToDB(sql)
        return results

    def get_all_proxy(self):
        proxy_set = set()
        proxyall = ProxyAll()
        redisproxy = proxyall.get_redis_all()
        mimvpproxy = proxyall.getProxyFromMimvp(1000)
        daxiangproxy = proxyall.getProxyFromDaxiang(1000)
        xiciproxy1 = proxyall.getProxyFromXICIOnePage(1)
        xiciproxy2 = proxyall.getProxyFromXICIOnePage(2)
        mysqlproxy = self.get_mysql_proxy()
        proxy_set = proxy_set.union(mysqlproxy, redisproxy, mimvpproxy, daxiangproxy, xiciproxy1, xiciproxy2)
        self.logger.info("all proxy size is:{}".format(len(proxy_set)))
        self.proxy_set = proxy_set
        return proxy_set

    def get_can_use_proxy(self):
        count = 0
        use_proxy = set()
        for proxy in self.proxy_set:
            proxy_ = self.checking_proxy(proxy)
            use_proxy.add(proxy_)
            if len(use_proxy) > 20:
                count = count + 1
                if count == 1:
                    sql = "delete from proxy_pool"
                    self.mysqlutils.ExeSqlToDB(sql)
                sql = "insert into proxy_pool(proxy) values ('%s')"
                self.mysqlutils.ExeSqlMany(sql, use_proxy)
                use_proxy.clear()
        if len(use_proxy) > 0:
            sql = "insert into proxy_pool(proxy) values ('%s')"
            self.mysqlutils.ExeSqlMany(sql, use_proxy)
            use_proxy.clear()


class DetailThreadRun(MThreadingRun):
    def __init__(self, num):
        self.cnki = WanfangProxy()
        super(DetailThreadRun, self).__init__(num)
        self.config = "./db.ini"
        self.myredisset = MyRedis(self.config)
        self.myredisset.set_redis_from_config(sesc="proxysetwanfangjournal")
        self.myredisset.conn_redis()
        self.myredisset.get_pipeline()

    @ThreadPoolManger.thread_lock
    def getTask(self, *args, **kwargs):
        self.myredisset.delete(self.myredisset.RedisKey)
        proxy_set = self.cnki.get_all_proxy()
        return proxy_set

    def setTask(self, results=None, *args, **kwargs):
        for url_tasks in results:
            # 将每一页加入任务队列
            self.add_job(self.func, url_tasks)
        time.sleep(10 * 60)

    @ThreadPoolManger.thread_lock
    def dealresult(self, *args, **kwargs):
        sql = "replace into proxy_pool(`proxy`) values (%s)"
        self.cnki.mysqlutils.ExeSqlMany(sql, self.results)
        self.myredisset.sadd(self.myredisset.RedisKey, set(self.results))

    def setProxy(self, proxysList=None):
        pass

    def is_break(self):
        return False

    def thread_pool_hook(self, threadinfo: ThreadInfo):
        # 设置代理线程不重启，默认会重启
        if threadinfo.get_thread_name() == self.etn.proxythreadname:
            threadinfo.set_is_restart(False)
        if threadinfo.get_thread_name() == self.etn.taskthreadname:
            threadinfo.set_is_restart(False)
        return {}

    def fun(self, threadval, *args, **kwargs):
        standardid = args[0]
        proxys = self.cnki.checking_proxy(standardid)
        if proxys != "":
            threadval.result_queue.put(proxys)


def main():
    down = DetailThreadRun(40)
    down.run()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
# @Time    : 2020/6/23 14:38
# @Author  : suhong
# @File    : wp_proxy_all.py
# @Software: PyCharm

"""
云代理 开放代理 刷新验证进入redis (db3 wp_proxy_all)
"""
import json
import random
import time

from re_common.baselibrary.utils.core.requests_core import USER_AGENTS

from re_common.facade.mysqlfacade import MysqlUtiles

from re_common.baselibrary.mthread.mythreading import ThreadInfo, ThreadVal, ThreadPoolManger

from re_common.baselibrary.mthread.MThreadingRun import MThreadingRun

from re_common.baselibrary.utils.baserequest import BaseRequest

from re_common.baselibrary.utils.myredisclient import MyRedis


class ProxyAll(object):
    def __init__(self, config="./db.ini"):
        self.config = config
        self.myredis = MyRedis(configpath=self.config, sesc='wp_proxy',is_conn_or_pipe=False)
        # self.myredis.get_pipeline()
        self.myredis.builder()

        self.Headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        self.baserequest = BaseRequest()
        self.ProxyPoolTotal = set()
        self.starttime = time.time()
        self.mysqlutils_proxy = MysqlUtiles('./db.ini', "db_proxy")

    def get_redis_all(self):
        return self.myredis.getDataFromRedis()

    def get_proxy_ip3366(self, num=600):
        proxyPool = set()
        # url = "http://gea.ip3366.net/api/?key=20200622135212736&getnum={}&order=1&formats=2&proxytype=01".format(num)
        url = "http://gea.ip3366.net/api/?key=20200622135212736&getnum={}&formats=2&proxytype=01".format(num)
        try:
            bools, estring, r = self.baserequest.base_request(url,
                                                              headers=self.Headers,
                                                              marks=['Ip'])
            if bools:
                json_data = json.loads(r.text)
                for info in json_data:
                    proxy = info['Ip'] + ":" + str(info['Port'])
                    proxyPool.add(proxy)

                return True, proxyPool

            return False, proxyPool
        except Exception as e:
            print(e)
            return False, proxyPool


class YanzhengThreadRun(MThreadingRun):
    def __init__(self, num):
        super(YanzhengThreadRun, self).__init__(num)
        self.pro = ProxyAll()
        self.yz_right_set = set()
        self.is_clean_redis = False


    def getTask(self, *args, **kwargs):
        return []

    def setTask(self, results=None, *args, **kwargs):

        if self.thread_pool.work_queue.is_empty():

            redis_proxypool = self.pro.get_redis_all()
            self.is_clean_redis = True
            if time.time() - self.pro.starttime <= 5:
                time.sleep(6 - (time.time() - self.pro.starttime))
            bools, proxypool = self.pro.get_proxy_ip3366()
            result_pro = proxypool.union(redis_proxypool)
            if bools:
                for raw in result_pro:
                    self.add_job(self.func,raw)
            self.pro.starttime = time.time()


    def dealresult(self, *args, **kwargs):
        if self.is_clean_redis:
            # 清理reids
            self.pipe.delete(self.pro.myredis.RedisKey)
            self.is_clean_redis = False

        # 处理self.yz_right_set集合
        print('Write DataBase %s ...' % self.pro.myredis.RedisKey)
        self.pipe.sadd(self.pro.myredis.RedisKey, *self.results)
        curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.pipe.hset('update_time', self.pro.myredis.RedisKey, curTime)
        self.pipe.execute()
        # 插入mysql
        for raw in self.results:
            self.deal_sql(raw)

    @ThreadPoolManger.thread_lock
    def deal_sql(self,raw):
        # 插入mysql统计每天获取的代理个数
        sql = "insert into gongwangproxy(proxy,cishu) Values('{}',1) on DUPLICATE key update cishu=cishu+1".format(raw)
        self.pro.mysqlutils_proxy.ExeSqlToDB(sql)



    def setProxy(self, proxysList=None):
        pass

    def is_break(self):
        return False

    def thread_pool_hook(self, threadinfo: ThreadInfo):
        # 设置代理线程不重启，默认会重启
        # if threadinfo.get_thread_name() == self.etn.proxythreadname:
        #     threadinfo.set_is_restart(True)
        # if threadinfo.get_thread_name() == self.etn.taskthreadname:
        #     threadinfo.set_is_restart(False)
        return {}

    def fun(self, threadval: ThreadVal, *args, **kwargs):
        """
        验证代理有效性,百度
        """
        raw = args[0]
        result_queue = threadval.get_result_queue()
        ppp = {
            'http': raw,
            'https': raw
        }
        try:
            url = "https://www.baidu.com/"
            bools, e, r = self.pro.baserequest.base_request(url,
                                                            headers=self.pro.Headers,
                                                            proxies=ppp,
                                                            timeout=5,
                                                            marks=['百度一下，你就知道'])
            if bools:
                result_queue.put(raw)
        except Exception as e:
            print(e)

        # 验证超星期刊
        # yzurl = "http://qikan.chaoxing.com/mag/infos?mags=ea15bb11cfca2424ae72402ca8461604"
        # mags = "ea15bb11cfca2424ae72402ca8461604"
        # HEADER = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #     'User-Agent': random.choice(USER_AGENTS),
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Referer': 'http://qikan.chaoxing.com',
        # }
        # HEADER['Referer'] = 'http://qikan.chaoxing.com/mag/infos?mags=' + mags
        # try:
        #     BoolResult, errString, r = self.pro.baserequest.base_request(url=yzurl,
        #                                                            headers=HEADER,
        #                                                            timeout=(5, 10),
        #                                                            proxies=ppp,
        #                                                            marks=['Fbookright fl'])
        #     if BoolResult:
        #         result_queue.put(raw)
        # except Exception as e:
        #     print(e)


if __name__ == '__main__':
    # p = ProxyAll()
    # p.get_redis_all()
    yz = YanzhengThreadRun(40)
    yz.run()
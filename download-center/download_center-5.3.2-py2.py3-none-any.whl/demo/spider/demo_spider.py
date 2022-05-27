# -*- coding: utf-8 -*-
import hashlib
import json
import os
import string
import sys
import random
import base64
import time
import traceback
import uuid
import urllib
import urllib.parse
from http import cookiejar

from urllib.request import Request, HTTPCookieProcessor, build_opener

from scrapy.http.cookies     import CookieJar

from download_center.new_spider.downloader.downloader import SpiderRequest
from download_center.new_spider.spider.basespider import BaseSpider
from download_center.util.util_log import UtilLogger

# 线上测试
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("PROJECT_PATH", PROJECT_PATH)
sys.path.append(PROJECT_PATH)
# sys.path.append(os.path.join(PROJECT_PATH, 'demo'))
# from demo.extractor.baidu_extractor import BaiduExtractor
# from extractor.baidu_extractor import BaiduExtractor


class DemoSpider(BaseSpider):
    def __init__(self, remote=True):
        super(DemoSpider, self).__init__(remote=remote)
        self.log = UtilLogger('DemoSpider', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_demo_spider'))
        # self.ext = BaiduExtractor()
        self.downloader.reset_ip()

    def get_user_password(self):
        return 'zhangbz', 'Welcome#1'

    def tn(self):
        return random.choice(
            ['50000021_hao_pg', 'site888_3_pg', '77021190_cpr', 'site5566', '520com_pg', '51010079_cpr'])

    # 'url': 'https://www.baidu.com/s?%s' % (urllib.parse.urlencode({'word': '联想', 'ie': 'utf-8', 'tn': self.tn()})),
    def start_requests(self):
        try:
           for i in range(1000):
               urls = [{
                   'url': 'https://m.baidu.com/s?%s' % (urllib.parse.urlencode({'word': '联想','pn':10})),
                   'type': 17,
                   'unique_key':self.get_unique_key()#默认md5 url 字段，不写则表示相同链接只查一次
               }]
               headers = {
                   "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Mobile Safari/537.36",
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   # 'Accept-Language':'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7,ar-XB;q=0.6,ar;q=0.5',
                   'Cookie': self.get_baidu_mb_cookie()
               }
               config={"param": {'cu':'https://www.baidu.com'},"conf_district_id":3}
               request = SpiderRequest(headers=headers, urls=urls,config=config)
               self.sending_queue.put(request)
               time.sleep(0.1)

        except Exception:
            self.log.error('获取初始请求出错: {}'.format(traceback.format_exc()))


    #获取百度移动端cookie
    def get_baidu_mb_cookie(self):
        cookies = None
        try:
            cookie_jar = cookiejar.CookieJar()
            request = Request('https://m.baidu.com/tc?tcreq4log=1', headers={})
            handlers = [HTTPCookieProcessor(cookie_jar)]
            opener = build_opener(*handlers)
            opener.open(request, timeout=10)
            for cookie in cookie_jar:
                if cookie.name == 'BDORZ':
                    cookies = 'BDORZ=' + cookie.value
                    break
        except Exception:
            pass
        return cookies

    #获取百度pc 端cookie
    def get_baidu_pc_cookie(self):
        letters_one = []
        letters_two = []
        for _ in range(32):
            letters_one.append(random.choice(string.ascii_uppercase + string.digits))

        for _ in range(27):
            letters_two.append(random.choice(string.lowercase + string.digits))

        return 'BAIDUID=%s:FG=1' % (''.join(letters_one)) + '; ' + 'BA_HECTOR=%s' % (''.join(letters_two))

    def get_stores(self):
        # 存储器
        stores = list()
        return stores

    def deal_response_results_status(self, task_status, url, result, request):
        """
        Args:
            task_status:
            url:
            result:
            request:

        Returns:
        根据自己的解析类型做不同的处理，默认返回html
        """
        if task_status == '2':
            config = request.config
            try:
                # result = json.loads(result["result"])
                if '联想' not in result["result"]:
                    print("结果抓取失败")
                else:
                    print("成功!，长度：{},url：{}".format(len(result), url['url']))
            except Exception as e:
                print('失败！url：{}'.format( url['url']))

            # rdata = self.ext.ext ractor(result["result"])
            # self.store_queue.put(result)
            # if isinstance(rdata, int):
            #     print("request ua: {}".format(request.headers["User-Agent"]))
            # else:
            #     result_d, include, keyword_list = rdata
            #     print(result_d)
            #     print(include)
            #     print(keyword_list)
            #
            # with open("html_py3_3.txt", 'w', encoding="utf-8") as f:
            #     f.write(result["result"])
        else:
            self.log.info('抓取失败: {}'.format(url))

    def to_store_results(self,  results, stores):
        """
        结果存储按需使用
        :return:
        """
        pass


def main():
    spider = DemoSpider(remote=True)
    spider.run(1, 1, 1, 1, record_log=True)   # 测试
    # spider.run(spider_count=1000, record_log=True)
    # spider.run(record_log=True)               # error



if __name__ == '__main__':
    main()

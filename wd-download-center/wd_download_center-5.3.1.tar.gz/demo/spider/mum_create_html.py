# -*- coding:utf-8 -*-
"""
@Time : 2021/10/15 13:09
@Author: LiADai(李晗)
@File : huawei_bankuai_page_spider.py
@ 版块下帖子链接/帖子title抓取，并标注发帖时间/是否加V或精华、热门帖
"""
import ssl

import requests

from demo.spider import config

ssl._create_default_https_context = ssl._create_unverified_context
import logging
import os
import urllib3
import warnings
import sys
from queue import Queue
import random
import time
from download_center.new_spider.downloader.downloader import SpiderRequest
from download_center.new_spider.spider.basespider import BaseSpider
from demo.store.py_store_mysql_pool import StoreMysqlPool

urllib3.disable_warnings()
warnings.filterwarnings('ignore')
file_name = os.path.basename(__file__).split('.')[0]
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)
logging.basicConfig(filename='{}/logs/{}.log'.format(PROJECT_PATH, file_name), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s : %(message)s')

class mum_creat_tool(BaseSpider):
    def __init__(self, remote=True):
        super(mum_creat_tool, self).__init__(remote)
        #版块下的数据，只允许访问2K条，登录也没用
        self.dataList = [
            {"name":"荣耀Magic系列","path":"https://club.hihonor.com/cn/forum-3965-{}.html?filter=lastpost","page":369},
            {"name":"荣耀数字系列","path":"https://club.hihonor.com/cn/forum-3484-{}.html?filter=lastpost","page":183},
            {"name": "荣耀V系列", "path": "https://club.hihonor.com/cn/forum-3159-{}.html?filter=lastpost", "page": 69},
            {"name": "荣耀X系列", "path": "https://club.hihonor.com/cn/forum-4280-{}.html?filter=lastpost", "page": 45},
            {"name": "荣耀Play系列", "path": "https://club.hihonor.com/cn/forum-3666-{}.html?filter=lastpost", "page": 14},
            {"name": "荣耀畅玩系列", "path": "https://club.hihonor.com/cn/forum-4526-{}.html?filter=lastpost", "page": 4},
            {"name": "问题反馈", "path": "https://club.hihonor.com/cn/forum-4508-{}.html?filter=lastpost", "page": 69},
            {"name": "荣耀亲选", "path": "https://club.hihonor.com/cn/forum-154-{}.html?filter=lastpost", "page": 2},
            {"name": "智能家居", "path": "https://club.hihonor.com/cn/forum-1835-{}.html?filter=lastpost", "page": 4},
            {"name": "智能穿戴", "path": "https://club.hihonor.com/cn/forum-4301-{}.html?filter=lastpost", "page": 10},
            {"name": "公测内测", "path": "https://club.hihonor.com/cn/forum-4149-{}.html?filter=lastpost", "page": 3},
            {"name": "Magic UI 4.0", "path": "https://club.hihonor.com/cn/forum-455-{}.html?filter=lastpost","page": 7},
            {"name": "使用技巧", "path": "https://club.hihonor.com/cn/forum-3667-{}.html?filter=lastpost", "page": 4},
            {"name": "荣耀云服务", "path": "https://club.hihonor.com/cn/forum-4522-{}.html?filter=lastpost", "page": 1},
            {"name": "爱美食", "path": "https://club.hihonor.com/cn/forum-713-{}.html?filter=lastpost", "page": 46},
            {"name": "爱旅行", "path": "https://club.hihonor.com/cn/forum-721-{}.html?filter=lastpost", "page": 41},
            {"name": "爱运动", "path": "https://club.hihonor.com/cn/forum-910-{}.html?filter=lastpost", "page": 47},
            {"name": "爱主题", "path": "https://club.hihonor.com/cn/forum-1053-{}.html?filter=lastpost", "page": 113},
            {"name": "爱游戏", "path": "https://club.hihonor.com/cn/forum-4400-{}.html?filter=lastpost", "page": 31},
            {"name": "爱摄影", "path": "https://club.hihonor.com/cn/forum-141-{}.html?filter=lastpost", "page": 470},
            {"name": "慢生活", "path": "https://club.hihonor.com/cn/forum-64-{}.html?filter=lastpost", "page": 12},
            {"name": "荣耀电竞堂", "path": "https://club.hihonor.com/cn/forum-1046-{}.html?filter=lastpost", "page": 1},
            {"name": "王者荣耀", "path": "https://club.hihonor.com/cn/forum-4513-{}.html?filter=lastpost", "page": 4},
            {"name": "使命召唤手游", "path": "https://club.hihonor.com/cn/forum-4514-{}.html?filter=lastpost", "page": 28},
            {"name": "穿越火线", "path": "https://club.hihonor.com/cn/forum-4515-{}.html?filter=lastpost", "page": 1},
            {"name": "QQ飞车手游", "path": "https://club.hihonor.com/cn/forum-4516-{}.html?filter=lastpost", "page": 1},
            {"name": "荣耀同城", "path": "https://club.hihonor.com/cn/forum-267-{}.html?filter=lastpost", "page": 2},
            {"name": "荣耀高校", "path": "https://club.hihonor.com/cn/forum-4346-{}.html?filter=lastpost", "page": 1},
            {"name": "荣耀创意精英挑战赛", "path": "https://club.hihonor.com/cn/forum-4528-{}.html?filter=lastpost", "page": 1},
            {"name": "大V申请", "path": "https://club.hihonor.com/cn/forum-150-{}.html?filter=lastpost", "page": 35},
            {"name": "申诉建议", "path": "https://club.hihonor.com/cn/forum-152-{}.html?filter=lastpost", "page": 3},
            {"name": "笔记本", "path": "https://club.hihonor.com/cn/forum-4333-{}.html?filter=lastpost", "page": 16},
            {"name": "平板", "path": "https://club.hihonor.com/cn/forum-4529-{}.html?filter=lastpost", "page": 22},
            {"name": "耳机音箱", "path": "https://club.hihonor.com/cn/forum-3719-{}.html?filter=lastpost", "page": 4}
        ]
        self.table_name = "huawei_bankuai_page"
        #User-Agent
        self.pc_useragent_list = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1",
            "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        ]

        #链接数据库
        try:
            self.db_225_connect = StoreMysqlPool(**config.db_225_test)
        except:
            self.db_225_connect = StoreMysqlPool(**config.db_225_test)
        self.store_queue = Queue()

    #请求页面
    def start_requests(self):
       sql = 'SELECT id,url FROM mum_url WHERE `status` = 0 limit 10;'
       data = self.db_225_connect.query(sql)
       for id,url  in data:
           self.id = id
           headers = {
               "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "User-Agent": random.choice(self.pc_useragent_list),
               "Cookie":"VONA_COMMON_LOG_KEY=8b16f212-f212-764e-470d-b0b5d5a2aed8; VONALOGID=881c783d432ddf2cd36f254f29bafa41; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217ceeb79ca317-067dc9a3b6ad32-57b193e-2073600-17ceeb79ca4640%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%2217ceeb79ca317-067dc9a3b6ad32-57b193e-2073600-17ceeb79ca4640%22%7D; krt.vis=92970e09-4014-4ef6-8c50-516b5cc659c6; Hm_lvt_c86e2c4bb4ad01427261d9484e89bf8b=1636092584; Hm_lpvt_c86e2c4bb4ad01427261d9484e89bf8b=1636092584; CUSTCD=; CustomerCode=; wechat_binded=; AUTHPHONE=; MISUMIVONAEC=%7b%22ABt%22%3a%22b%22%7d; VONAEC_TOP_WOS_BALOON=opened; depocity=%5b119%2c224%2c257%2c289%2c317%2c340%5d; Qs_lvt_294485=1636092584; Qs_pv_294485=2514124822837465600; _ga=GA1.3.2007463036.1636092584; _gid=GA1.3.216996045.1636092584; krt.context=session%3a84134014-1b92-4af6-b8cc-8e4096bb34fe%3bcontext_mode%3aother; _dc_gtm_UA-143948235-1=1; _ga-ch=GA1.3.2007463036.1636092584; _ga-ch_gid=GA1.3.506639854.1636092585; _dc_gtm_UA-6311415-1=1; _gaexp=GAX1.3.sG8KycnKQaK90ZtJ3XtaGQ.19014.0; _gat=1; mediav=%7b%22eid%22%3a%2267947%22%2c%22ep%22%3a%22%22%2c%22vid%22%3a%22%22%2c%22ctn%22%3a%22%22%2c%22vvid%22%3a%22%22%2c%22_mvnf%22%3a1%2c%22_mvctn%22%3a0%2c%22_mvck%22%3a1%2c%22_refnf%22%3a1%7d",
               "Host":"www.misumi.com.cn"
           }
           # requests.get(url=url,headers=headers,verify=False)
           spider_request = SpiderRequest(headers=headers, urls=url,config={"redirect": 1})
           self.sending_queue.put(spider_request)

           self.db_225_connect.do('UPDATE mum_url SET `status` = 1 WHERE id = {};'.format(self.id))
           time.sleep(1)
           break

    #详情返回
    def deal_response_results_status(self, task_status, url, result, request):
        if task_status == '2':
            ext_type = url["ext_type"]
            print("详情返回成功。。。")
            if ext_type==2:
                res = self.get_details_info(url, result['result'])
        else:
            print("下载中心方法失败")

    # 详情处理
    def get_details_info(self, url, html):
        print(self.id)
        print(html)
        pass


    #下载中心 用户账号、密码
    def get_user_password(self):
        return "test", "Welcome#1"
        # return 'caihaijun', 'caihaijun'

    def is_start(self):
        return self.sended_queue.qsize() < self.sended_queue_maxsize and self.sending_queue.qsize() < self.sended_queue_maxsize \
               and self.response_queue.qsize() < self.sended_queue_maxsize





if __name__ == "__main__":
    spider = mum_creat_tool(remote=True)
    timeout_time = -1  # 永不停止 18秒 停止
    process_pool = 5  # 线程数 debug用单线程
    spider.run(1, 1, 1, 1, timeout_time, timeout_time, timeout_time,
               timeout_time, True)







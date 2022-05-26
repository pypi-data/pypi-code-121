# -*- coding:utf-8 -*-
# author:jackwu 
# time:2022/5/26
# description: 案例使用
import os
import sys

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)

from hgj_download_center.downloader.downloader import SpiderRequest
from hgj_download_center.downloader.new_basespider import NewBaseSpider


class  DemoTest(NewBaseSpider):
    def __init__(self):
        super(DemoTest, self).__init__(task_name="task", use_redis=False)

    def start_requests(self):
        url = "https://www.baidu.com"
        headers = {
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
            }
        urls = [{"url": url, "method": "GET", "retry_num": 1}]
        request = SpiderRequest(headers=headers,urls=urls)
        self.sending_queue.put(request)

    def deal_response_results_status(self, task_status, url, result, request):
        if task_status == 2:
            print(result["result"])


if __name__ == '__main__':
    a = DemoTest()
    a.run(1, 1, 1, 1)
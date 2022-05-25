#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 19:53
# @Author  : Adyan
# @File    : scheduler.py


from scrapy_redis import defaults
from scrapy_redis.scheduler import Scheduler


class ResetScheduler(Scheduler):
    def next_request(self):
        """
            scrapy-redis调度器，用于从队列调度下一个请求。
        """
        if len(self) > 0:
            block_pop_timeout = self.idle_before_close
            try:
                request = self.queue.pop(block_pop_timeout)
            except:
                request = None
            if request and self.stats:
                self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        # 如果 request 队列为空，则从 start_urls 队列拿数据生成请求
        else:
            request = self.get_next_request_from_url()
        return request

    def get_next_request_from_url(self):
        """
            从 start_urls 队列取数据生成请求
        """
        use_set = self.spider.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        fetch_one = self.server.spop if use_set else self.server.rpop
        start_urls_key = self.spider.name + ':start_urls'
        data = fetch_one(start_urls_key)
        if not data:
            # Start_urls queue empty.
            return None
        req = self.spider.make_request_from_data(data)
        if req:
            return req
        else:
            return None

    def __len__(self):
        try:
            return len(self.queue)
        except:
            return 0

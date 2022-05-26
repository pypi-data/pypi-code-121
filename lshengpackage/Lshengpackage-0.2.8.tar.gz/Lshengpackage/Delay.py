# !/usr/bin/env python
# -*-coding:utf-8 -*-


import time
import random


class Delay:
    @classmethod
    def delay(cls, rand_start_time=0.3, rand_end_time=0.8):
        """
        随机延迟, 默认 0.5 ~ 1 之间随机
        :return:
        """
        random.seed(time.time())
        rand_time = random.uniform(rand_start_time, rand_end_time)
        time.sleep(rand_time)


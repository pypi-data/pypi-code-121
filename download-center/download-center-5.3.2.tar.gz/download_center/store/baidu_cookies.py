# -*- coding: utf8 -*-

import redis
import time
from download_center.store import config


class baiduCookie(object):
    def __init__(self):
        self.redisPool = redis.ConnectionPool(**(config.DOWNLOADER_CENTER_REDIS[config.ENVIR]))
        self.redisClient = redis.StrictRedis(connection_pool=self.redisPool)
        self.pc_cookie_key = 'baidu:pc:cookies'
        self.mb_cookie_key = 'baidu:mb:cookies'

    def getCookies(self, num=0, key_name='pc'):
        '''
        [获取一个有效的cookie 正序]
        :param num:
        :param key_name:
        :return:
        '''
        # noinspection PyBroadException
        try:
            if key_name == 'pc':
                return self.redisClient.zrange(self.pc_cookie_key, 0, num)
            elif key_name == 'mb':
                return self.redisClient.zrange(self.mb_cookie_key, 0, num)
            else:
                return []
        except Exception:
            return []

    def getLastCookies(self, num=0, key_name='pc'):
        '''
         [获取最新的cooie]
        :param num:
        :param key_name:
        :return:
        '''
        # noinspection PyBroadException
        try:
            if key_name == 'pc':
                return self.redisClient.zrevrange(self.pc_cookie_key, 0, num)
            elif key_name == 'mb':
                return self.redisClient.zrevrange(self.mb_cookie_key, 0, num)
            else:
                return []
        except Exception:
            return []

    def addCookies(self, cookie, key_name='pc'):
        '''
        [添加一个值]
        :param cookie:
        :param key_name:
        :return:
        '''
        # noinspection PyBroadException
        try:
            score = int(round(time.time() * 1000))
            if key_name == 'pc':
                return self.redisClient.zadd(self.pc_cookie_key, {cookie: score})
            elif key_name == 'mb':
                return self.redisClient.zadd(self.mb_cookie_key, {cookie: score})
            else:
                return 0
        except Exception:
            return 0

    def delCookies(self, cookie, key_name='pc'):
        '''
        删除cookie
        :param cookie:
        :return:
        '''
        # noinspection PyBroadException
        try:
            if key_name == 'pc':
                return self.redisClient.zrem(self.pc_cookie_key, cookie)
            elif key_name == 'mb':
                return self.redisClient.zrem(self.mb_cookie_key, cookie)
            else:
                return 0
        except Exception:
            return 0

    def totalCookies(self, key_name='pc'):
        '''
        [统计个数]
        :return:
        '''
        # noinspection PyBroadException
        try:
            if key_name == 'pc':
                return self.redisClient.zcard(self.pc_cookie_key)
            elif key_name == 'mb':
                return self.redisClient.zcard(self.mb_cookie_key)
            else:
                return 0
        except Exception:
            return 0


if __name__ == '__main__':
    bc = baiduCookie()
    print(bc.getCookies(1, 'p'))
    print(bc.totalCookies('mb'))

# -*- coding: utf-8 -*-
# 用于过滤重复的item
# @Author  : white.tie
# @Time    : 2022/4/29 14:21
# @File: bloomfilter.py.py
"""
date:2021/10/26
auth:t.y.jie
changed: by zhizhong 2022/5/10

params:: 
from scrapy.cfg :: REDIS_HOST / REDIS_PORT / REDIS_DB / REDIS_PASSWORD <str>
from custom_settings :: Data_Size <int/str>  eg: 1000*10000/百万级/千万级/千万 
from custom_settings :: Aim_Set <dict>  eg: {"title","all_json"} 除重依据字段
"""
import redis
import os
from hashlib import md5
from scrapy.utils.conf import get_config
from bisect import bisect_left
from scrapy.exceptions import DropItem


class SimpleHash(object):
    # cap 代表向量长度
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        # 位运算保证最后的值在0到self.cap之间
        return (self.cap-1) & ret



class BloomFilterPipeline(object):
    def __init__(self, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD,REDIS_BF_KEY,REDIS_BIT,Aim_Set):
        """
        :param host: the host of Redis
        :param port: the port of Redis
        :param db: witch db in Redis
        :param blockNum: one blockNum for about 90,000,000; if you have more strings for filtering, increase it.
        :param key: the key's name in Redis
        """
        self.server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
        self.bit_size = 1 << REDIS_BIT  # Redis的String类型最大容量为512M，现使用256M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = REDIS_BF_KEY
        self.blockNum = 1
        self.hashfunc = []
        self.aim_set = Aim_Set
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    @classmethod
    def from_crawler(cls, crawler):
        # 判断运行环境<根据环境变量中是否配置IF_PROD=True,或 测试正式环境settings["IF_PROD"] = True>
        # section_select ="redis_cfg_prod" if os.environ.get('IF_PROD') == "True" or crawler.settings.get('IF_PROD')\
        #      == True or get_config().get("settings","IF_PROD",fallback="False")=="True" else "redis_cfg_dev"
        section_select ="redis_cfg_prod" if os.environ.get('IF_PROD') == "True" \
             or get_config().get("settings","IF_PROD",fallback="False")=="True" else "redis_cfg_dev"
        Data_Size = crawler.settings.get('Data_Size')
        if isinstance(Data_Size,int):
            REDIS_BIT = [25,28,31][bisect_left([101*10000,1000*10000,10000*10000], Data_Size)]
        elif isinstance(Data_Size,str):
            means ='十万' if '十万' in Data_Size else ('百万' if '百万' in Data_Size else ("千万" if "千万" in Data_Size else  "亿"))
            REDIS_BIT = {"十万":24,"百万":25,"千万":28,"亿":31,}.get(means)
        else:
            REDIS_BIT = 28
        return cls(REDIS_HOST=get_config().get(section=section_select,option='REDIS_HOST',fallback='') or crawler.settings.get('REDIS_HOST'),
                REDIS_PORT = get_config().getint(section=section_select,option='REDIS_PORT',fallback='') or crawler.settings.get('REDIS_PORT'),
                REDIS_PASSWORD = get_config().get(section=section_select,option='REDIS_PASSWORD',fallback='')or \
                    crawler.settings.get('REDIS_PASSWORD') or crawler.settings.get('REDIS_PARAMS',{}).get("password"),
                REDIS_DB = get_config().get(section=section_select,option='REDIS_DB',fallback='') or \
                    crawler.settings.get('REDIS_DB') or crawler.settings.get('REDIS_PARAMS',{}).get("db"),
                REDIS_BF_KEY = crawler.spidercls.name,
                REDIS_BIT=REDIS_BIT,
                Aim_Set = crawler.settings.get('Aim_Set',{"title","sources","brand_name", "brand_id", "package", "list_json", "category_id",
                                                 "p_category_id", "contain_json", "all_json",
                                                 "raw_img_url", "raw_pdf_url"})
                )

    def isContains(self, str_input):    
        if not str_input:
            return False
        m5 = md5()
        m5.update(str_input)
        str_input = m5.hexdigest()
        ret = True
        # 获取键名 bloomfilter0
        name = self.key
        for f in self.hashfunc:
            offset = f.hash(str_input)
            # 命令用于对 key 所储存的字符串值，获取指定偏移量上的位(bit)。
            ret = ret & self.server.getbit(name, offset)
        return ret

    def insert(self, str_input):
        m5 = md5()
        m5.update(str_input)
        str_input = m5.hexdigest()
        # name redis键的名称
        name = self.key
        for f in self.hashfunc:
            offset = f.hash(str_input)
            self.server.setbit(name, offset, 1)
            
    def iter_dict_total(self,item_dic):
        """
        @param item_dic: 输入一个字典按照字符串排序
        @return: 输出字典转化为字符串
        """
        item_ls = []
        
        def iter_dict(item_dic):
            # aim_set 目标字段与 item_dic 字段交集
            for key in sorted(self.aim_set&set(item_dic)):
                value = item_dic[key]
                item_ls.append(key)
                if isinstance(value, dict):
                    iter_dict(value)
                elif isinstance(value, list):
                    for value_ in value:
                        iter_dict(value_)
                elif isinstance(value, set):
                    for value_ in value:
                        iter_dict(value_)
                else:
                    item_ls.append(str(value))
                value = None
            return "".join(item_ls).encode()

        return iter_dict(item_dic)
    
    def process_item(self, item, spider):
        postItem = dict(item)
        item_str = self.iter_dict_total(postItem)
        msg = item.get("title", "") or item.get("category_name","") or item.get("url","") or item.get("sources","") # or item.get("")
        if self.isContains(item_str):  # 判断字符串是否存在
            DropItem(f'This is item exists! info: {msg}')
        else:
            self.insert(item_str)
            return item

    def close_spider(self,spider):
        self.server.close()

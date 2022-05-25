"""
date:2021/10/26
auth:t.y.jie
"""
import json
import pymongo
from pymongo import MongoClient,ReadPreference
from scrapy.utils.conf import get_config
import os
import logging
from datetime import datetime

class MongodbPipeline(object):
    def __init__(self,MONGO_HOST,MONGO_PORT,MONGO_PSW,MONGO_USER,MONGO_DB,AUTH_SOURCE,SECTION_SELECT):
        # 链接数据库
        if MONGO_PORT:
            # 兼容之前的settings配置
            mongo_url = 'mongodb://{0}:{1}@{2}:{3}/?authSource={4}&authMechanism=SCRAM-SHA-1'.format(MONGO_USER, MONGO_PSW,
                                                                                                     MONGO_HOST, MONGO_PORT,
                                                                                                     AUTH_SOURCE)
            self.client = MongoClient(mongo_url)
            self.db = self.client[MONGO_DB]  # 获得数据库的句柄
        else:
            mongo_url = 'mongodb://{0}:{1}@{2}/?authSource={3}&replicaSet=rs01'.format(MONGO_USER, MONGO_PSW,
                                                                                                     MONGO_HOST,
                                                                                                     AUTH_SOURCE)
            self.client = MongoClient(mongo_url)
            # 读写分离
            self.db = self.client.get_database(MONGO_DB, read_preference=ReadPreference.SECONDARY_PREFERRED)
        print("mongo_url:",mongo_url)
        self.section_select = SECTION_SELECT
    @classmethod
    def from_crawler(cls, crawler):
        # 判断运行环境<根据环境变量中是否配置IF_PROD=True,或 测试正式环境settings["IF_PROD"] = True>
        section_select ="mongo_cfg_prod" if os.environ.get('IF_PROD') == "True" or crawler.settings.get('IF_PROD')\
             == True or get_config().get("settings","IF_PROD",fallback="False")=="True" else "mongo_cfg_dev"
        
        return cls(MONGO_HOST=get_config().get(section=section_select,option='MONGO_HOST',fallback='') or crawler.settings.get('MONGO_HOST'),
                   MONGO_PORT=get_config().getint(section=section_select,option='MONGO_PORT',fallback='') or crawler.settings.get('MONGO_PORT'),
                   MONGO_PSW=get_config().get(section=section_select,option='MONGO_PSW',fallback='') or crawler.settings.get('MONGO_PSW'),
                   MONGO_USER=get_config().get(section=section_select,option='MONGO_USER',fallback='') or crawler.settings.get('MONGO_USER'),
                   MONGO_DB=get_config().get(section=section_select,option='MONGO_DB',fallback='') or crawler.settings.get('MONGO_DB'),
                   AUTH_SOURCE=get_config().get(section=section_select,option='AUTH_SOURCE',fallback='') or crawler.settings.get('AUTH_SOURCE'),
                   SECTION_SELECT = section_select)

    def process_item(self, item, spider):
        date_time = datetime.now().strftime("_%Y_%m_%d") if self.section_select=='mongo_cfg_prod' else ""
        postItem = dict(item)
        if postItem.get("brand_id", None):  # brand_id :: int
            postItem["brand_id"] = int(postItem["brand_id"])
        if postItem.get("level", None):  # level :: int
            postItem["level"] = int(postItem["level"])
        if postItem.get("list_json", None):  # list_json :: json
            if isinstance(postItem["list_json"], dict):
                postItem["list_json"] = json.dumps(dict(postItem["list_json"]))
        if postItem.get("min_work_tp",None):  # min_work_tp :: int
            postItem["min_work_tp"] = int(postItem["min_work_tp"])
        if postItem.get("max_work_tp",None):  # max_work_tp :: int
            postItem["max_work_tp"] = int(postItem["max_work_tp"])
        if postItem.get("moq", None):  # moq :: int
            postItem["moq"] = int(postItem["moq"].replace(",",''))
        if postItem.get("mpq", None):  # mpq :: int
            postItem["mpq"] = int(postItem["mpq"].replace(",",''))
        if postItem.get("rough_weight", None):  # rough_weight :: float #注意单位是g
            postItem["rough_weight"] = int(postItem["rough_weight"])
        if postItem.get("title", None):  # title :: 去两端空格
            postItem["title"] = postItem["title"].strip()
        if postItem.get("sources",None):  # sources :: 去两端空格
            postItem["sources"] = postItem["sources"].strip()
        if postItem.get("brand_name", None):  # brand_name :: 去两端空格
            postItem["brand_name"] = postItem["brand_name"].strip()
        if postItem.get("category_id", None):  # category_id :: 去两端空格
            postItem["category_id"] = postItem["category_id"].strip()
        if postItem.get("category_name", None):  # category_name :: 去两端空格
            postItem["category_name"] = postItem["category_name"].strip()
        if postItem.get("brand_id", None):  # brand_id :: int
            postItem["brand_id"] = int(postItem["brand_id"])
        if postItem.get("level", None):  # level :: int
            postItem["level"] = int(postItem["level"])
        if postItem.get("list_json", None):  # list_json :: json
            if isinstance(postItem["list_json"], dict):
                postItem["list_json"] = json.dumps(dict(postItem["list_json"]))
        if postItem.get("min_work_tp",None):  # min_work_tp :: int
            postItem["min_work_tp"] = int(postItem["min_work_tp"])
        if postItem.get("max_work_tp",None):  # max_work_tp :: int
            postItem["max_work_tp"] = int(postItem["max_work_tp"])
        if postItem.get("moq", None):  # moq :: int
            postItem["moq"] = int(postItem["moq"])
        if postItem.get("mpq", None):  # mpq :: int
            postItem["mpq"] = int(postItem["mpq"])
        if postItem.get("rough_weight", None):  # rough_weight :: float #注意:单位g
            postItem["rough_weight"] = float(postItem["rough_weight"])
        msg = postItem.get("title", "") or postItem.get("category_name","") or postItem.get("url","") or postItem.get("sources","") # or postItem.get("")
        try:
             # 把item转化成字典形式
            coll = self.db[item.table+date_time]
            coll.insert(postItem)  # 向数据库插入一条记录
            logging.debug(f'Crawl {msg} done.' )
        except pymongo.errors.DuplicateKeyError:
            logging.info(f'去重 {msg} Skip .') 
        return item

    def close_spider(self,spider):
        self.client.close()

from scrapy.utils.conf import get_config
import pymysql
from pymysql.err import IntegrityError,OperationalError

import logging
import json,os,re

class MySQLPipeline:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        # 判断运行环境<根据环境变量中是否配置IF_PROD=True,或 测试正式环境settings["IF_PROD"] = True>
        section_select ="mysql_cfg_prod" if os.environ.get('IF_PROD') == "True" or crawler.settings.get('IF_PROD')\
             == True or get_config().get("settings","IF_PROD",fallback="False")=="True" else "mysql_cfg_dev"
        # 取 scrapy.cfg 参与配置
        return cls(host=get_config().get(section=section_select,option="MYSQL_HOST",fallback='') or crawler.settings.get('MYSQL_HOST'),
            database=get_config().get(section=section_select,option='MYSQL_DATABASE',fallback='') or crawler.settings.get('MYSQL_DATABASE'),
            user=get_config().get(section=section_select,option='MYSQL_USER',fallback='') or crawler.settings.get('MYSQL_USER'),
            password=get_config().get(section=section_select,option='MYSQL_PASSWORD',fallback='') or crawler.settings.get('MYSQL_PASSWORD'),
            port=get_config().getint(section=section_select,option='MYSQL_PORT',fallback='') or crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = dict(item)
        if data.get("title", None):  # brand_id :: 出去型号两边空格
            data["title"] = data["title"].strip()
        if data.get("sources", None):  # sources :: 出去sources两边空格
            data["sources"] = data["sources"].strip()
        if data.get("brand_name", None):  # brand_name :: 出去品牌两边空格
            data["brand_name"] = data["brand_name"].strip()
        if data.get("category_name", None):  # category_name :: 去两端空格
            data["category_name"] = data["category_name"].strip()
        if data.get("category_id", None):  # category_id :: 出去category_id两边空格
            data["category_id"] = data["category_id"].strip()
        if data.get("brand_id", None):  # brand_id :: int
            data["brand_id"] = int(data["brand_id"])
        if data.get("level", None):  # level :: int
            data["level"] = int(data["level"])
        if data.get("list_json", None):  # list_json :: json
            if isinstance(data["list_json"], dict):
                data["list_json"] = json.dumps(dict(data["list_json"],ensure_ascii=False))
        if data.get('sources',None):  # source 来源转小写
            data['sources'] = data['sources'].strip().lower()
        if data.get("min_work_tp",None):  # min_work_tp :: int
            data["min_work_tp"] = int(data["min_work_tp"])
        if data.get("max_work_tp",None):  # max_work_tp :: int
            data["max_work_tp"] = int(data["max_work_tp"])
        if data.get("moq", None):  # moq :: int
            data["moq"] = int(data["moq"].replace(",",''))
        if data.get("mpq", None):  # mpq :: int
            data["mpq"] = int(data["mpq"].replace(",",''))
        if data.get("rough_weight", None):  # rough_weight :: float #注意单位是g
            data["rough_weight"] = int(data["rough_weight"])
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (item.table, keys, values)
        msg = data.get("title", "") or data.get("category_name","") or data.get("url","") or data.get("sources","") # or data.get("")
        try:
            self.db.ping(reconnect=True)
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
            logging.debug(f'Crawl {msg} done.' )
        except IntegrityError:
            self.db.rollback()
            logging.info(f'去重 {msg} Skip .') 
        except OperationalError as e:
            logging.warning(e.args[1])
            column = re.findall("Unknown column '(.*?)' in 'field list'",e.args[1])[0]
            logging.warning(f"字段 {column} 在数据库中未创建，请自查后重试！ ")
        return item
import scrapy
import jsw_nx as nx
from fake_useragent import UserAgent


class BaseSpider(scrapy.Spider):
    handle_httpstatus_list = [400]
    url = None
    ua = UserAgent()
    ua_pc = 'Mozilla/5.0 zgrab/0.x'
    ua_mobile = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) By aric.zheng/0.x'
    ua_random = ua.chrome
    support_crawling = False

    @classmethod
    def is_crawled_complete(cls, **kwargs):
        entity_class = kwargs.get('entity_class')
        crawled = kwargs.get('crawled', {'is_crawled': False})
        return entity_class.where(crawled).count() == 0

    @classmethod
    def get_un_crawled(cls, **kwargs):
        # required:
        entity_class = kwargs.get('entity_class')
        # crawl + optional:
        crawled = kwargs.get('crawled', {'is_crawled': False})
        crawling_opts = {'is_crawling': False} if cls.support_crawling else {}
        options = nx.mix(crawled,kwargs.get('options', crawling_opts))
        limit = kwargs.get('limit', None)

        if limit:
            records = entity_class.where(options).take(limit).get()
        else:
            records = entity_class.where(options).get()

        # start crawling, update is_crawling
        if cls.support_crawling:
            for record in records:
                record.is_crawling = True
                record.save()

        return records

    @classmethod
    def update_crawled(cls, **kwargs):
        record = kwargs.get('record')
        crawled = kwargs.get('crawled', 'is_crawled')
        setattr(record, crawled, True)
        record.save()

    @classmethod
    def noop_request(cls):
        yield scrapy.Request(url="https://www.baidu.com", callback=nx.noop_scrapy_parse)

from scrapy import signals
import json


class DemoLogger:
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.stats)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_closed(self, spider, reason):
        spider.logger.info(
            json.dumps(
                {
                    "eventType": "ScrapyCrawlSummary",
                    "spider": f"{spider.settings['BOT_NAME']}/{spider.name}",
                    "item_scraped_count": self.stats.get_value("item_scraped_count", 0),
                }
            )
        )

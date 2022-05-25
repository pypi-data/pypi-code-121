from scrapy.xcc_downloadermiddlewares.fake_ua import choice_brower_model

class RandomUserAgent(object):
    DEFAULT_BROWSER = 'chrome'

    def __init__(self, uabrowser):
        self.browser = uabrowser  # if self.uabrowser else self.DEFAULT_BROWSER

    @classmethod
    def from_crawler(cls, crawler):
        ub = crawler.settings.get('UABROWSER')
        return cls(uabrowser=ub)

    def process_request(self, request, spider):
        request.headers["User-Agent"] = choice_brower_model(browser=self.browser)

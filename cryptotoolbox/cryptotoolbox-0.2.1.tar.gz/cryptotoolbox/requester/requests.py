import requests


class Get(object):
    def __init__(self, flag):
        self.flag = flag
        self.connector = None
    def __call__(self, original_func):
        def wrappee(connector, **kwargs):
            self.connector = connector
            original_func(self.flag)
        return wrappee


    def __fill_request(self):
        self.connector


class Connector(object):
    def __init__(self):
        self.__hello = "Hugo"

    @property
    def hello(self):
        return self.__hello

    @Get("https://www.bitmex.com/api/v1/orderBook/L2?symbol=xbt&depth=100000")
    def get_prices(self, **kwargs):
        return requests.get(**kwargs)


if __name__ == '__main__':
    a = Connector().get_prices(url="coucou")

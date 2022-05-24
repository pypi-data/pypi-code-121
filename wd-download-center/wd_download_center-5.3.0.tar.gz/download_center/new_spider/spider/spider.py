# -*- coding: utf8 -*-
import os
import re
import sys



class SpiderDownloader(object):
    """
    下载器的抽象类
    用于下载指定url的网页内容
    下载器可能自身具备下载功能，也可能是作为与下载中心交互的接口
    """

    def __init__(self):
        pass

    def set(self, headers, config={}, urls=[]):
        """
        设置http头或者将相关配置发到下载中心
        Args:
            headers: 字典，http头信息，
                举例，{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
            config: 字典，可为空，用于向下载中心发送下载类型、优先级、抓取频率等相关信息，
                或者向下载函数设置超时等相关信息，
                举例：{'type':0, 'priority':5, 'frequency':1} 或 {'timeout':10}
            urls: 数组，不使用下载中心则为空，用于将待下载的url预先发到下载中心进行下载
        Returns:
            1: 正常, 0: 出错
        """
        return 0

    def get(self, url):
        """
        下载特定url的页面或者向下载中心请求特定url的结果
        Args:
            url: 要获取结果的一个url
        Returns :
            None: 未取到结果，可能是下载中心还没有下载完成
            文本: 下载结果
        """
        return None


class SpiderExtractor(object):
    """
    解析器的抽象类
    用于将特定网页解析成结构化信息
    每个页面有一个独立的SpiderExtractor类
    """

    def __init__(self):
        pass

    def extractor(self, text):
        """
        将一个页面文本解析为结构化信息的字典
        Args:
            text: 需要解析的文本
        Returns:
            数组: 每条为一个完整记录，记录由字典格式保存
        """
        return []


class SpiderStore(object):
    """
    存储器的抽象类
    用于将结构化信息保存到指定存储媒介中
    Attributes:
        fields: 用于保持抽取器字典的key与数据库字段的对应关系，
            如果结果字典的某个key不包含在fields中，则将直接使用key作为字段名
    """

    def __init__(self):
        self.fields = {}
        pass

    def store(self, results, type=1, keys=[]):
        """
        将一个数组存储到指定的存储媒介中
        Args:
            reuslts: 数组，每条为一个完整记录，记录由字典格式保存
            type: 1-只插入（出错则忽略），2-只更新（原记录不存在则忽略），3-插入更新（无记录则插入，有记录则更新）
            keys: 只插入则为空，更新则存储关键字典，此字段将作为更新的where条件
        Returns:
            1: 正常, 0: 出错
        """
        pass


class Spider(object):
    """
    爬虫的抽象类
    Attributes:
        headers: http头，同SpiderDownloader
        config: 抓取配置，同SpiderDownloader
        urls: 待抓取url，同SpiderDownloader
        downloader: 下载器，通常一个Spider配一个下载器
        extractor: 解析器，一个Spider可以配多个解析器
        store: 存储器，通常一个Spider配一个存储器
    """

    def __init__(self):
        self.headers = {}
        self.config = {}
        self.urls = []
        self.downloader = SpiderDownloader()
        self.extractor = SpiderExtractor()
        self.store = SpiderStore()
        pass

    def get_seeds(self):
        """
        获取urls
        """
        f = open('seeds.txt')
        for line in f:
            self.urls.append(line[:-1])
        f.close()

    def prepare(self):
        """
        用于对接下载中心的异步抓取，作为独立操作运行，投递任务后即退出
        """
        self.get_seeds()
        self.downloader.set(self.headers, self.config, self.urls)

    def run(self):
        """
        运行主函数，可独立运行（独立下载器模式），也可放在prepare之后运行（下载中心模式）
        """
        self.get_seeds()
        for url in self.urls:
            content = self.downloader.get(url)
            results = self.extractor.extractor(content)
            if len(results) > 0:
                self.store.store(results)

    def test(self, url):
        """
        测试单体url的结果
        """
        content = self.downloader.get(url)
        results = self.extractor.extractor(content)
        print(results)


"""
def Main():
    s = Spider()
    #s.prepare
    s.run()

if __name__ == "__main__":
    Main();
"""

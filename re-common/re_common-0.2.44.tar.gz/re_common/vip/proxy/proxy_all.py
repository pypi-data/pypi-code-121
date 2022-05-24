import re

from bs4 import BeautifulSoup

from re_common.baselibrary.utils.baserequest import BaseRequest
from re_common.baselibrary.utils.baseurl import BaseUrl
from re_common.baselibrary.utils.myredisclient import MyRedis


class ProxyAll(object):

    def __init__(self, config="./db.ini"):
        self.config = config
        self.myredis = MyRedis(self.config)
        self.myredis.set_redis_from_config()
        self.myredis.conn_redis()
        self.Headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        self.baserequest = BaseRequest()

    def get_redis_all(self):
        return self.myredis.getDataFromRedis()

    def getProxyFromMimvp(self, num=600):
        r""" 从 http://proxy.mimvp.com/ 获取代理地址 """
        # http://proxy.mimvp.com/api/fetch.php?orderid=860160414114016557&num=100&http_type=1&anonymous=3&ping_time=1&transfer_time=5
        url = 'http://proxy.mimvp.com/api/fetch.php'
        dicts = {
            "orderid": "860161011165812474",
            "num": num,
            "http_type": "1",  # 协议类型（http）
            "anonymous": "2,3,5",  # 提取透明，匿名+欺骗，高匿
            "ping_time": "1",  # 响应时间
            "transfer_time": "5",  # 传输速度
        }
        url = BaseUrl.dicts_to_url(dicts, url=url)

        proxyPool = set()

        BoolResult, errString, r = self.baserequest.base_request(url, headers=self.Headers, timeout=10)
        if not BoolResult:
            return proxyPool

        lst = r.text.split('\n')
        for line in lst:
            line = line.strip()
            if line.count('.') == 3:
                proxyPool.add(line)
        return proxyPool

    # 从 http://tpv.daxiangdaili.com 获取代理地址，<- 大象代理
    # http://tpv.daxiangdaili.com/ip/?tid=556923006054759&num=1000
    def getProxyFromDaxiang(self, num):
        url = 'http://tpv.daxiangdaili.com/ip/'
        dicts = {
            "tid": "556923006054759",
            "num": num,
            # "filter":"on",
            "foreign": "all",
            "delay": "5"  # 延迟时间
        }
        url = BaseUrl.dicts_to_url(dicts, url=url)

        proxyPool = set()

        BoolResult, errString, r = self.baserequest.base_request(url, headers=self.Headers, timeout=10)
        if not BoolResult:
            return proxyPool

        # print('daili666:' + repr(r.text))
        lst = r.text.split('\n')
        for line in lst:
            line = line.strip()
            if line.count('.') == 3:
                proxyPool.add(line)

        return proxyPool

    # 从http://www.xici.net.co/nn/获取代理地址
    # pageNum表示采集第几页
    def getProxyFromXICIOnePage(self, pageNum):
        ProxyPool = set()

        url = 'http://www.xicidaili.com/nn/'
        if pageNum > 1:
            url += str(pageNum)

        proxyPool = set()
        BoolResult, errString, r = self.baserequest.base_request(url, headers=self.Headers, timeout=10)
        if not BoolResult:
            return proxyPool

        html = r.content.decode('utf-8')

        soup = BeautifulSoup(html, 'html.parser')
        ipTable = soup.find('table', id='ip_list')
        if not ipTable:
            print('Error: not ipTable')
            return set()

        for trTag in ipTable.find_all('tr'):
            lst = list(trTag.find_all('td'))
            if len(lst) != 10:
                continue
            ip = ''.join(lst[1].stripped_strings)
            port = ''.join(lst[2].stripped_strings)
            item = ip + ':' + port
            if re.match(r'^[\d\.:]+$', item):
                ProxyPool.add(item)
        return ProxyPool

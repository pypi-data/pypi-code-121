# -*- coding: utf8 -*-
import json
import os
import re
import sys
import random
import time
import base64
import traceback
from unit.get_baidu_cookie import baiduCookie

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'keyword_pulldown_monitoring'))


class BaiduSpiderPublicFun(object):
    """
    解析百度移动端，获取片名，real_url,rank
    """

    def __init__(self):
        super(BaiduSpiderPublicFun, self).__init__()
        self.baidu_cookie = baiduCookie()

    # 获取移动端ua
    def get_mobile_useragent(self):
        mobile_useragent_list = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/533.36",
            "Mozilla/5.0 (Linux; U; Android 5.0.2; zh-CN; Letv X501 Build/DBXCNOP5501304131S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/10.10.0.800 U3/0.8.0 Mobile Safari/534.30",
            "Mozilla/5.0 (Linux; U; Android 5.0.2; zh-cn; Letv X501 Build/DBXCNOP5501304131S) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.7 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 5.1.1; vivo X6S A Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3 baiduboxapp/7.3.1 (Baidu; P1 5.1.1)",
            "Mozilla/5.0 (Linux; U; Android 4.3; zh-cn; N5117 Build/JLS36C) AppleWebKit/534.24 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.24 T5/2.0 baiduboxapp/7.0 (Baidu; P1 4.3)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X; zh-CN) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/13D15 UCBrowser/10.9.15.793 Mobile",
            "Mozilla/5.0 (iPhone 6p; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/6.0 MQQBrowser/6.7 Mobile/13D15 Safari/8536.25 MttCustomUA/2",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1",
            "Mozilla/5.0 (Linux; U; Android 4.1.2; zh-cn; GT-S7572 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.7 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; SM-J3109 Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.6 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; Coolpad 8297-T01 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.6 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 5.1.1; zh-CN; MX4 Pro Build/LMY48W) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/10.10.0.800 U3/0.8.0 Mobile Safari/534.30",
            "Mozilla/5.0 (Linux; Android 5.1; m2 note Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.114 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 5.1; zh-CN; m2 note Build/LMY47D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/10.9.10.788 U3/0.8.0 Mobile Safari/534.30",
            "Mozilla/5.0 (Linux; U; Android 5.1; zh-cn; m2 note Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.6 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; CHM-CL00 Build/CHM-CL00) AppleWebKit/534.24 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.24 T5/2.0 baiduboxapp/7.1 (Baidu; P1 4.4.4)",
            "Mozilla/5.0 (Linux; Android 5.0.1; HUAWEI GRA-TL00 Build/HUAWEIGRA-TL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36 MxBrowser/4.5.9.3000",
            "Mozilla/5.0 (Linux; Android 5.0.1; HUAWEI GRA-CL00 Build/HUAWEIGRA-CL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3 baiduboxapp/7.3.1 (Baidu; P1 5.0.1)",
            "Mozilla/5.0 (Linux; Android 5.0.2; Redmi Note 2 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3 baiduboxapp/7.3.1 (Baidu; P1 5.0.2)",
            "Mozilla/5.0 (Linux; Android 4.4.4; Che1-CL10 Build/Che1-CL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3 baiduboxapp/7.3.1 (Baidu; P1 4.4.4)",
            "Mozilla/5.0 (Linux; U; Android 4.4.2; zh-cn; HUAWEI P6-C00 Build/HuaweiP6-C00) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.7 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 4.3; R7007 Build/JLS36C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3 baiduboxapp/7.3.1 (Baidu; P1 4.3)",
            "Mozilla/5.0 (Linux; Android 5.1.1; KIW-CL00 Build/HONORKIW-CL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/7.1 baidubrowser/7.1.12.0 (Baidu; P1 5.1.1)",
        ]
        return random.choice(mobile_useragent_list)

    # 获取pc端ua
    def get_pc_useragent(self):
        pc_useragent_list = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1",
            "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        ]
        return random.choice(pc_useragent_list)

    # 获取pc端请求头
    def get_pc_headers(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'www.baidu.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            "Sec-Fetch-Dest": "document",
            'User-Agent': self.get_pc_useragent(),
            "Cookie": self.get_cook("1"),
            # "Cookie": 'BAIDUID=8BDD3E2AD9CD40385EBDE14EF60838B3:FG=1; BIDUPSID=8BDD3E2AD9CD403861768216F9752CD4; PSTM=1591698880; BD_UPN=133352; MSA_WH=375_667; H_WISE_SIDS=148078_147939_153647_150685_150076_147091_141744_150083_151862_148867_151312_153682_150745_147280_153629_153435_153289_153755_151016_151559_153567_146574_148523_151032_127969_153227_146548_152902_152982_146652_154013_146732_153058_154001_150764_131423_152022_152116_114553_147527_152931_107320_152716_140367_153502_144966_154061_153116_154118_139883_153060_153951_147546_153985_148869_150667_154293_151944_110085_154151; plus_cv=1::m:49a3f4a6; COOKIE_SESSION=79448_0_4_4_12_6_0_0_2_3_0_1_79441_0_2_0_1597988999_0_1597988997%7C9%23139428_11_1597280665%7C8; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; plus_lsv=f56cb9af77cd7927; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1596432006,1597041078,1597286977,1597829277; BDRCVFR[gltLrB7qNCt]=mk3SLVN4HKm; delPer=0; BD_CK_SAM=1; rsv_i=2e46h8wdTj%2BhIW6U2Gun2sXfuu%2B4N79z1KB5tZZqscDcn0kzK%2BlHTOt61lFWIg8HGIBm2u7uVMHMxQv0pu92gWvYzJY2VWA; bd_af=1; SE_LAUNCH=5%3A26632993; FEED_SIDS=3000066_2; PSINO=5; kleck=5b193409d1a773576320fcef7a87b3c5; H_PS_PSSID=1465_32571_32328_32351_32045_32116_26350_32495_32482; H_PS_645EC=c1f4AXgdjLxePW6H13Q2cdn5tSiEbdYfbbvvwuO4cnCIBkSOBht8ohKoxWI; WWW_ST=1598001346785',
        }
        return headers

    # 获取移动端请求头
    def get_mb_headers(self):
        headers = {
            'Host': 'm.baidu.com',
            'User-Agent': random.choice(self.get_mobile_useragent()),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://m.baidu.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Cookie': self.get_cook("2"),
        }
        return headers

    # 获取公用库百度cookie
    def get_cook(self, device):
        """
        获取有效的cookie
        :return:
        """
        if device == '1':
            key_name = 'pc'
        else:
            key_name = 'mb'
        for i in range(2):
            if self.baidu_cookie.totalCookies(key_name=key_name) > 0:
                cookie = str(self.baidu_cookie.getLastCookies(key_name=key_name)[0], encoding="utf-8")
                return cookie
            else:
                print('no cookie')
                return 'BAIDUID={}:FG=1'.format(time.time())
        return ''

    # 拆解任务url
    def judge_url(self, ckurl):
        """
        判断url是否是一个json字符串，如果是返回一个由url组成的list
        :param ckurl:
        :return:
        """
        url_list = list()
        if ckurl.startswith("["):
            try:
                ckurl = ckurl.replace("\\'", "\"")
                url_list = json.loads(ckurl)
            except:
                print(traceback.format_exc())
                print("-------------")
                print(ckurl)
                url_list.append(ckurl)
        else:
            ckurl = ckurl.replace("'", "\"")
            url_list.append(ckurl)
        return url_list

    # 格式化pc端入库html
    def format_pc_html_save(self, html):
        html = html.replace("https://www.baidu.com/img/flexible/logo/pc/result.png",
                            "img/flexible/logo/pc/result.png") \
            .replace("//www.baidu.com/img/flexible/logo/pc/result.png", "img/flexible/logo/pc/result.png") \
            .replace('https://www.baidu.com/img/flexible/logo/pc/result@2.png', "img/flexible/logo/pc/result@2.png") \
            .replace('//www.baidu.com/img/flexible/logo/pc/result@2.png', "img/flexible/logo/pc/result@2.png")
        return str(base64.b64encode(html.encode(encoding="utf-8")), encoding="utf-8")

    # 格式化移动端入库html
    def format_mb_html_save(self, html):
        html = html.replace('position: fixed; display: flex; bottom: 0px; left: 0px; z-index: 300;', 'display:none;') \
            .replace('https://www.baidu.com/img/flexible/logo/logo_web.png', "img/flexible/logo/logo_web.png") \
            .replace('//www.baidu.com/img/flexible/logo/logo_web.png', "img/flexible/logo/logo_web.png")
        return str(base64.b64encode(html.encode(encoding="utf-8")), encoding="utf-8")

    # 判断pc端dom元素是否异常
    def check_pc_dom_is_error(self, html):
        if html.find("</html>") < 0 or html.find('id="wrap"') >= 0 or (
                "<title>百度App</title>" in html and "拦截通用" in html) or (
                "<title>百度安全验证</title>" in html and "百度安全验证" in html) or html.find('页面不存在_百度搜索') >= 0 or html.find(
            'id="container"') < 0 or html.find('id="content_left"') < 0 or html.find('<title>') < 0:
            return True
        else:
            return False

    # 判断移动端dom元素是否异常
    def check_mb_dom_is_error(self, html):
        if html.find("</html>") < 0 or html.find('id="results"') < 0 or (
                "<title>百度App</title>" in html and "拦截通用" in html) or (
                "<title>百度安全验证</title>" in html and "百度安全验证" in html) or html.find('页面不存在_百度搜索') >= 0 \
                or html.find('<title>') < 0:
            return True
        else:
            return False


if __name__ == '__main__':
    pass

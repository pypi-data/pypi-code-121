from re_common.baselibrary.utils.basehttpx import BaseHttpx
from re_common.baselibrary.utils.baserequest import BaseRequest
import re

url = "https://www.ip.cn/"


def basehttpx_test_ip(proxy):
    patten = "<code>(.*?)</code>"
    bshttpx = BaseHttpx()
    BoolResult, errString, r = bshttpx.base_sn_httpx(url=url,
                                                     proxies=proxy,
                                                     headers="")
    ip = re.findall(patten,r.text)
    if len(ip) == 0:
        print(r.text)
    else:
        print(ip)

def baserequest_test_ip(proxy):
    patten = "Your IP</span>: (.*?)</span>"
    bsrequests = BaseRequest()
    bsrequests.is_use_proxy(True)
    bsrequests.set_proxy(proxy)
    BoolResult, errString, r = bsrequests.base_request(url=url)
    ip = re.findall(patten, r.text)
    if len(ip) == 0:
        print(r.text)
    else:
        print(ip)


if __name__ == '__main__':
    basehttpx_test_ip("192.168.31.176:8012")
    baserequest_test_ip("192.168.31.176:8012")
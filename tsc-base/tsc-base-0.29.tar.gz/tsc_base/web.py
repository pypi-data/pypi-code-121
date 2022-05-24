import http.client
import hashlib
import urllib
import time
import random
import json


def bd_translate(q, id, secretKey, QPS=1., fromL='auto', toL='zh', delay=0):
    """
    百度翻译api, 因为QPS所以单用户不可以多进程并行
    :param q: str or list; 查询
    :param id: str; 填写你的appid
    :param secretKey: str; 填写你的密钥
    :param QPS: float; 每秒查询率上限
    :param fromL: str; 原文语种
    :param toL: str; 译文语种
    :param delay: None or float; 最后一次q的等待时间(秒)，None表示和QPS一致。防止没必要的空等待
    :return: list or None,int,list[dict]; 查询结果列表(错误则返回None),查询失败数量,所有result
    """
    if isinstance(q, str):
        q = [q]
    if delay is None:
        delay = 1 / QPS
    dst_L = []  # 查询结果列表(错误则返回None)
    numNone = 0  # 查询失败数量
    result_L = []  # 所有result
    httpClient = None
    myurl = '/api/trans/vip/translate'
    for i, qi in enumerate(q):
        salt = random.randint(32768, 65536)
        sign = hashlib.md5((id + qi + str(salt) + secretKey).encode()).hexdigest()
        myurl_ = f"{myurl}?appid={id}&q={urllib.parse.quote(qi)}&from={fromL}&to={toL}&salt={salt}&sign={sign}"
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')  # 注意 http 明文
            httpClient.request('GET', myurl_)
            result = json.loads(httpClient.getresponse().read().decode("utf-8"))
        except Exception as e:
            result = {'error_code': e}
        finally:
            if httpClient:
                httpClient.close()
        if 'trans_result' in result:
            dst_ = []
            for j in result['trans_result']:
                dst_.append(j['dst'])
            dst = '\n'.join(dst_)
        else:
            print(result)
            dst = None
            numNone += 1
        dst_L += [dst]
        result_L.append(result)
        if i < len(q) - 1:
            time.sleep(1 / QPS)
    time.sleep(delay)
    return dst_L, numNone, result_L

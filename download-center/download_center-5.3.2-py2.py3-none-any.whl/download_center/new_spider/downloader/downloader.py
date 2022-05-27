# -*- coding: utf8 -*-
import json
from datetime import datetime
from datetime import timedelta
import traceback
import base64
import time
import hashlib
from threading import Timer

import pymysql

import urllib3
urllib3.disable_warnings()
import requests

from pymysql.converters import escape_string

reqs = requests.session()
reqs.keep_alive = False

from download_center.new_spider.downloader import config  # py3
import sys


def util_md5(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


class Downloader(object):
    """
    通用下载器
    """

    def __init__(self, set_mode='db', get_mode='db', store_type=5):     # 兼容
        self.t = Timer(60*10, self.reset_ip)
        pass

    def reset_ip(self):
        """
        当接口调用失败后，重新ping以下网络情况，并更新接口地址
        :return:
        """
        try:
            ip_type = 1 if config.ping(config.DOWNLOADER_CENTER_INNER_IP) else 2
            if ip_type == 2 :
                self.t.start()
            else:
                self.t.cancel()
            response = reqs.post(config.TASK_SCHEDULER_IP.format(config.IP_HOST), data={"type": ip_type}, timeout=config.REQUEST_TIMEOUT)
            config.downloader_ip = str(response.content).strip()
            print("current downloader_ip: {}".format(config.downloader_ip))
        except:
            time.sleep(60)
            print(traceback.format_exc())

    def downloader_add_black_ip(self, ip, type, expire_time=6):
        try:
            data = {"ip": ip, "type": type, "expire_time": expire_time}
            reqs.post(config.ADD_BLACK_IP.format(config.downloader_ip), data=data, timeout=config.REQUEST_TIMEOUT)
            return True
        except:
            print(traceback.format_exc())
            return False

    def validate_accout(self, user="", password=""):
        try:
            ip_type = 1 if config.ENVIR == 'inner' else 2
            data = {"user": user, "password": password, 'type': ip_type}
            for i in range(2):
                try:
                    r = reqs.post(config.VALIDATE_ACCOUNT_URL.format(config.DOWNLOADER_CENTER_IP[config.ENVIR]), data=data, timeout=config.REQUEST_TIMEOUT)
                    rdata = json.loads(r.text)
                    break
                except:
                    time.sleep(config.REQUEST_RETYR_SLEEP)
                    # print(traceback.format_exc())
                    rdata = {'status': 0,'msg':'login failure'}

            if rdata["status"] == 0:
                print(rdata["msg"])
                return False
            else:
                config.downloader_ip = rdata["ip"]
                return rdata["user_id"]
        except:
            print("datetime: {}; error: {}".format(str(datetime.now()), str(traceback.format_exc())))
            return False

    def set(self, request):
        """
        放任务
        Returns:
            正常: 返回字典，key值为每个url，value值0（失败）、  1（成功） 其它失败
            出错: 0 参数问题  -2 地域问题  -1 错误 1 正常

        請求異常 超時  返回正常， 其它根據返回狀態
        """
        try:
            data = {"user_id": request.user_id,
                    "headers": json.dumps(request.headers),
                    "config": json.dumps(request.config),
                    "urls": json.dumps(request.urls)
                    }
            for i in range(3):
                try:
                    rdata = reqs.post(config.DOWNLOADER_SENDTASK.format(config.downloader_ip), data=data, timeout=config.REQUEST_TIMEOUT)
                    r = json.loads(rdata.text)
                    break
                except:
                    # print(traceback.format_exc())
                    time.sleep(config.REQUEST_RETYR_SLEEP)
                    r = {'status': 0, 'msg': 'set failure'}

            if r["status"] == 1:
                rdata = json.loads(r["rdata"])
                for i, k in enumerate(rdata):
                    request.urls[i]["unique_md5"] = k
            else:
                print("set msg: {}".format(r["msg"]))
            return int(r["status"])
        except Exception:                                         # data exception
            print("datetime: {}; error: {}".format(str(datetime.now()), str(traceback.format_exc())))
            time.sleep(config.REQUEST_RETYR_MAX_SLEEP)

            self.reset_ip()
            for url in request.urls:
                if 'unique_key' in url.keys():
                    md5 = util_md5(escape_string(url['url']) + str(url['unique_key']))
                else:
                    md5 = util_md5(escape_string(url['url']))
                url['unique_md5'] = md5
            return -1

    def get(self, request):
        """
        向下载中心请求特定url的结果
        模式，redis->直接查询redis数据库，db->直接查询数据库，http->通过http接口查询
        Args:
            request: SpiderRequest对象
        """
        # noinspection PyBroadException
        try:
            data = {"user_id": request.user_id,
                    "config": json.dumps(request.config),
                    "urls": json.dumps(request.urls)
                    }
            for i in range(3):
                # noinspection PyBroadException
                try:
                    rdata = reqs.post(config.DOWNLOADER_GETRESULT.format(config.downloader_ip), data=data, timeout=config.REQUEST_TIMEOUT)
                    r = json.loads(rdata.text)
                    break
                except Exception:
                    r = {'status': 0,'msg':'reqs failure'}
                    # print(traceback.format_exc())
                    time.sleep(config.REQUEST_RETYR_SLEEP)

            if r["status"] == 1:
                unique_md5_results = json.loads(r["rdata"])
                for unique_md5 in unique_md5_results:
                    if 'result' in unique_md5_results[unique_md5] and unique_md5_results[unique_md5]['result']:
                        html = base64.b64decode(unique_md5_results[unique_md5]['result'])
                        if html and isinstance(html, bytes):
                            try:
                                html = html.decode(encoding="utf-8", errors='ignore')  # bytes to str
                            except:
                                pass
                        unique_md5_results[unique_md5]['result'] = html
                return unique_md5_results
            else:
                print("get error msg: {}".format(r["msg"]))
                return r["status"]
        except Exception:
            print("datetime: {}; error: {}".format(str(datetime.now()), str(traceback.format_exc())))
            time.sleep(config.REQUEST_RETYR_MAX_SLEEP)

            self.reset_ip()
            rdata = dict()
            for url in request.urls:
                rdata[url['unique_md5']] = {"status": 0}
            return rdata

class SpiderRequest(object):

    __slots__ = ['user_id', 'headers', 'config', 'urls']    # save memory

    def __init__(self, user_id=None, headers=dict(), config=dict(), urls=list()):
        self.user_id = user_id
        self.headers = headers
        self.config = config
        self.urls = urls

    def set_headers_key(self, key, value):
        self.headers[key] = value

    def set_headers(self, header):
        self.headers = header

    def set_config_key(self, key, value):
        self.headers[key] = value

    def set_config(self, set_configs):
        self.headers = set_configs


def main():
    spider = Downloader()
    # spider.validate_accout(user="test", password="Welcome#1")
    # spider.validate_accout(user="sunxiang", password="sxspider")
    spider.reset_ip()
    # req = SpiderRequest()
    # print(spider.get(req))

    # spider.downloader_add_black_ip("fihf", '11', expire_time=6)
    print(config.downloader_ip)


if __name__ == '__main__':
    main()



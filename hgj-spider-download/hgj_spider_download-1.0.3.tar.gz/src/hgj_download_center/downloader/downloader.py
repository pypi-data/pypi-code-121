# -*- coding: utf8 -*-
import traceback

import urllib3
try:
    from utils.util_normal import get_proxy_ip
except:
    pass
urllib3.disable_warnings()
import requests

reqs = requests.session()
reqs.keep_alive = False


class Downloader(object):
    """
    通用下载器
    """

    def __init__(self, task_name):
        self.task_name = task_name

    def get(self, request, timeout: int = 30, request_proxy=False):
        """获取页面Dom结果
        Args:
            request: SpiderRequest对象
        """
        try:
            req = request.urls[0]
            url = req["url"]
            method = req.get("method", "get").upper()             # 请求类型
            headers = request.headers                              # 请求头
            request_parms = req.get("request_parms", {})
            params = request_parms.get("params", None)            # 作为参数增加到URL中
            data = request_parms.get("data", None)                # POST时，data其格式必须为字符串
            json_ = request_parms.get("json", None)               # POST时，json数据，直接传dict
            verify = request_parms.get("verify", None)            # 验证
            proxies = request_parms.get("proxies", None)          # 代理
            if request_proxy:
                proxy_dict = get_proxy_ip()
                if proxy_dict:
                    proxies = {
                        "http": f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['ip']}:{proxy_dict['port']}",
                        "https": f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['ip']}:{proxy_dict['port']}"
                    }
                else:
                    print(f'{self.task_name} 获取代理ip失败')
            response = requests.request(method=method, url=url, headers=headers, params=params, data=data, json=json_,
                                    proxies=proxies, verify=verify, timeout=timeout)
            return {"success": True, "results": response}
        except requests.exceptions.ConnectTimeout:
            # 代理问题 连接超时
            print(traceback.format_exc())
        except Exception:
            print(traceback.format_exc())
            return {"success": False, "message": str(traceback.format_exc())}


class SpiderRequest(object):

    __slots__ = ['headers', 'config', 'urls']    # save memory

    def __init__(self, headers=dict(), config=dict(), urls=list()):
        self.headers = headers
        self.config = config
        self.urls = urls
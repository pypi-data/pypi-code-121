# @Time    : 2022/2/22 9:35
# @Author  : kang.yang@qizhidao.com
# @File    : request.py
import sys
from urllib import parse
import requests
import json as json_util
from qrunner.utils.config import conf
from qrunner.utils.log import logger

IMG = ["jpg", "jpeg", "gif", "bmp", "webp"]


def request(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        print("\n")
        logger.info('-------------- Request -----------------[🚀]')
        try:
            url = list(args)[1]
        except IndexError:
            url = kwargs.get("url", "")

        if "http" not in url:
            base_url = conf.get_item('common', 'base_url')
            if 'http' in base_url:
                url = parse.urljoin(base_url, url)
            else:
                logger.debug('请设置正确的base_url')
                sys.exit()

        img_file = False
        file_type = url.split(".")[-1]
        if file_type in IMG:
            img_file = True

        logger.debug("[method]: {m}      [url]: {u} \n".format(m=func_name.upper(), u=url))
        auth = kwargs.get("auth", "")

        # 处理请求头
        headers = conf.get_item('common', 'headers')  # 从配置文件拿到登录用户请求头
        # 如果login=False，从请求头中删掉登录态相关的键值对
        login_status = kwargs.get('login', True)
        if not login_status:
            login_key = conf.get_item('api', 'login_key')
            for key in login_key:
                headers.pop(key)
        # 把上层请求方法的headers参数更新到headers里面
        headers.update(kwargs.pop("headers", {}))
        kwargs['headers'] = headers

        # 设置请求超时时间为5s
        try:
            timeout_default = int(conf.get_item('common', 'timeout'))
        except:
            timeout_default = 10
        timeout_set = kwargs.pop("timeout", None)
        if timeout_set is not None:
            kwargs['timeout'] = timeout_set
        else:
            kwargs['timeout'] = timeout_default

        cookies = kwargs.get("cookies", "")
        params = kwargs.get("params", "")
        data = kwargs.get("data", "")
        json = kwargs.get("json", "")

        # running function
        r = func(*args, **kwargs)

        if auth != "":
            logger.debug(f"[auth]:\n {json_util.dumps(auth)} \n")
        logger.debug(f"[headers]:\n {r.request.headers} \n")
        if cookies != "":
            logger.debug(f"[cookies]:\n {json_util.dumps(cookies)} \n")
        if params != "":
            logger.debug(f"[params]:\n json: {json_util.dumps(params)} \n python: {params}")
        if data != "":
            logger.debug(f"[data]:\n json: {json_util.dumps(data)} \n python: {data}")
        if json != "":
            logger.debug(f"[json]:\n json: {json_util.dumps(json)} \n python: {json}")

        ResponseResult.status_code = r.status_code
        logger.info("-------------- Response ----------------")
        try:
            resp = r.json()
            logger.debug(f"[type]: json \n")
            logger.debug(f"[response]:\n {resp} \n")
            ResponseResult.response = resp
        except BaseException as msg:
            # 非json响应数据，最多打印100个字符
            logger.debug("[warning]: {} \n".format(str(msg)[:100]))
            if img_file is True:
                logger.debug("[type]: {}".format(file_type))
                ResponseResult.response = r.content
            else:
                logger.debug("[type]: text \n")
                logger.debug(f"[response]:\n {r.text[:100]} \n")
                ResponseResult.response = r.text

    return wrapper


class ResponseResult:
    status_code = 200
    response = None


class HttpRequest(object):

    @request
    def get(self, url, params=None, login=True, **kwargs):
        if "http" not in url:
            base_url = conf.get_item('common', 'base_url')
            if 'http' in base_url:
                url = parse.urljoin(base_url, url)
            else:
                logger.debug('请设置正确的base_url')
                sys.exit()
        return requests.get(url, params=params, **kwargs)

    @request
    def post(self, url, data=None, json=None, login=True, **kwargs):
        if "http" not in url:
            base_url = conf.get_item('common', 'base_url')
            logger.debug(base_url)
            if 'http' in base_url:
                url = parse.urljoin(base_url, url)
            else:
                logger.debug('请设置正确的base_url')
                sys.exit()
        return requests.post(url, data=data, json=json, **kwargs)

    @request
    def put(self, url, data=None, json=None, login=True, **kwargs):
        if "http" not in url:
            base_url = conf.get_item('common', 'base_url')
            if 'http' in base_url:
                url = parse.urljoin(base_url, url)
            else:
                logger.debug('请设置正确的base_url')
                sys.exit()
        if json is not None:
            data = json_util.dumps(json)
        return requests.put(url, data=data, **kwargs)

    @request
    def delete(self, url, login=True, **kwargs):
        if "http" not in url:
            base_url = conf.get_item('common', 'base_url')
            if 'http' in base_url:
                url = parse.urljoin(base_url, url)
            else:
                logger.debug('请设置正确的base_url')
                sys.exit()
        return requests.delete(url, **kwargs)

    @property
    def response(self):
        """
        Returns the result of the response
        :return: response
        """
        return ResponseResult.response

    @property
    def session(self):
        """
        A Requests session.
        """
        s = requests.Session()
        return s

    @staticmethod
    def request(method=None, url=None, headers=None, files=None, data=None,
                params=None, auth=None, cookies=None, hooks=None, json=None):
        """
        A user-created :class:`Request <Request>` object.
        """
        req = requests.Request(method, url, headers, files, data,
                               params, auth, cookies, hooks, json)
        return req


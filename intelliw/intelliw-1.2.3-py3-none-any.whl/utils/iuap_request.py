"""
iUAP HTTP auth protocol implementation
"""
import jwt
import time
import json
import math
import hashlib
import base64
import requests

from intelliw.utils.util import default_dump
from intelliw.config import config

requests.packages.urllib3.disable_warnings()

class Response:
    def __init__(self, status: int, body: str, error: Exception = None):
        self.status = status
        self.body = body
        self.error = error

    def raise_for_status(self):
        """
        raise :class:`IuapRequestException <IuapRequestException>` if status is not 200
        """
        if self.status != 200:
            msg = 'http request error, status: [{}], body: [{}] '.format(
                self.status, self.body)
            if self.error is not None:
                raise IuapRequestException(
                    msg + str(self.error)) from self.error
            raise IuapRequestException(msg)

    def __str__(self):
        return 'status: {}, body: {}, error: {}'.format(self.status, self.body, self.error)


class IuapRequestException(Exception):
    pass


def get(url: str, headers: dict = None, params: dict = None) -> Response:
    """
    get request

    :param url: request url
    :param headers: request headers
    :param params: request url params
    :return: Response
    """
    return sign_and_request(url, 'GET', headers, params)


def post_json(url: str, headers: dict = None, params: dict = None, data: object = None) -> Response:
    """
    post request, send data as json

    :param url: request url
    :param headers: request headers
    :param params: request url parameters
    :param data: request body. if data is not `str`, it will be serialized as json.
    :return: Response
    """

    if headers is None:
        headers = {}
    headers['Content-type'] = 'application/json; charset=UTF-8'

    body = None
    if data is not None:
        if isinstance(data, str):
            body = data.encode('UTF-8')
        else:
            body = json.dumps(data, default=default_dump,
                              ensure_ascii=False).encode('UTF-8')

    return sign_and_request(url, 'POST', headers, params, body)


def put_file(url: str, headers: dict = None, params: dict = None, data: object = None) -> Response:
    if headers is None:
        headers['Content-type'] = 'application/octet-stream'
    return sign_and_request(url, 'PUT', headers, params, data)


def post_form_urlencoded(url: str, headers: dict = None, params: dict = None, data: dict = None) -> Response:
    """
    post request, data will be send in x-www-form-urlencoded flavor

    :param url: request url
    :param headers: request headers
    :param params: request url parameters
    :param data: request body
    :return: Response
    """

    if headers is None:
        headers = {}
    headers['Content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

    sign_params = {}
    if params is not None and len(params) > 0:
        sign_params = params.copy()

    if data is not None and len(data) > 0:
        for item in data.items():
            sign_params[item[0]] = item[1]

    return sign_and_request(url, 'POST', headers, params, data, sign_params)


def sign_and_request(url: str,
                     method: str = 'GET',
                     headers: dict = None,
                     params: dict = None,
                     body: dict = None,
                     sign_params: dict = None) -> Response:
    """
    sign and do request

    :param url: request url, without query
    :param method: Http request method, GET, POST...
    :param headers: request headers
    :param params: parameters will be sent as url parameters. Also used to generate signature if sign_params is None.
    :param body: request body
    :param sign_params: params used to generate signature, if sign_params is None, signature will be generated base on params.
    :return: response body
    """
    if sign_params is not None:
        token = sign(url, sign_params)
    else:
        token = sign(url, params)

    if headers is None:
        headers = {}
    headers['YYCtoken'] = token

    return __do_request(url, method, headers, params, body)


def sign(url: str, params: dict) -> str:
    """
    generate iuap signature

    :param url: request url, without parameters
    :param headers: request headers
    :param params:  request parameters, x-www-form-urlencoded request's body parameters should also be included.
    :return: iuap signature
    """
    issue_at = __issue_at()
    sign_key = __build_sign_key(
        config.ACCESS_KEY, config.ACCESS_SECRET, issue_at, url)
    jwt_payload = {
        "sub": url,
        "iss": config.ACCESS_KEY,
        "iat": issue_at
    }
    if params is not None and len(params) > 0:
        sorted_params = sorted(params.items())
        for item in sorted_params:
            if item[1] is None:
                val = ''
            elif len(str(item[1])) >= 1024:
                val = str(__java_string_hashcode(str(item[1])))
            else:
                val = str(item[1])
            jwt_payload[item[0]] = val

    jwt_token = jwt.encode(jwt_payload, key=sign_key, algorithm='HS256')
    return str(jwt_token, encoding='UTF-8')


def __issue_at():
    issue_at = int(time.time())
    issue_at = math.floor(issue_at / 600) * 600
    return issue_at


def __build_sign_key(access_key, access_secret, access_ts, url):
    str_key = access_key + access_secret + str(access_ts * 1000) + url
    sign_key_bytes = hashlib.sha256(str_key.encode('UTF-8')).digest()
    return base64.standard_b64encode(sign_key_bytes).decode('UTF-8')


def __java_string_hashcode(s: str):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def __do_request(url: str,
                 method: str = 'GET',
                 headers: dict = None,
                 params: dict = None,
                 body: dict = None) -> Response:

    for i in range(1,5):
        try:
            resp = requests.request(method=method, url=url, params=params,data=body,headers=headers,verify=False)
            status_code = resp.status_code
            try:
                resp.encoding = "utf8"
                body = resp.content
            except UnicodeDecodeError:
                body = resp.content   
            return Response(status_code, body)
        except requests.exceptions.RequestException as e:
            if i == 4:
                raise e
            time.sleep(i*2)
            print(f"[request] requert retry time: {i}, url: {url}")
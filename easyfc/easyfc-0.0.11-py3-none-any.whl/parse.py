from urllib.parse import parse_qs, urlsplit
from json import loads


def get_params(environ: dict) -> tuple or dict:
    """
    获取请求param，返回给以dict
    :param environ: 函数计算场景值
    :return: dict 包含请求中param的dict
    """
    try:
        url = environ['fc.request_uri']
        query = urlsplit(url).query
        params = dict(parse_qs(query))
        key_list = params.keys()
        temp_params = {}
        for index in key_list:
            temp_params[index] = params[index][0]
        return temp_params
    except Exception as e:
        return e.args


def get_json(environ: dict) -> dict or tuple:
    """
    获取请求体内的json，返回给以dict
    :param environ: 函数计算场景值
    :return: dict 包含请求中json的dict
    """
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    try:
        # get param here
        request_body = environ['wsgi.input'].read(
            request_body_size).decode('utf-8')

        request_body = loads(request_body)
        return request_body
    except Exception as e:
        return e.args


def get_headers(environ: dict) -> dict or tuple:
    """
    获取请求的全部请求头，返回给以dict
    :param environ: 函数计算场景值
    :return: dict 包含所有请求头的dict
    """
    dic_ = {}
    try:
        for k, v in environ.items():
            if k.startswith('HTTP_'):
                dic_[k] = v
        return dic_
    except Exception as e:
        return e.args

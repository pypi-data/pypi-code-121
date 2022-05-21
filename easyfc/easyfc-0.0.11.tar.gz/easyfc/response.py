import json

from typing import List


class response:
    def __init__(self, data: dict, msg: str, code: str):
        self.data = data
        self.msg = msg
        self.code = code

    def parseJonsByte(self) -> List[bytes]:
        """
        输出标准返回体
        :return: 按照阿里函数计算格式，返回标准的List[bytes] 格式
        """
        dic_ = {
            'data': self.data,
            'msg': self.msg,
            'code': self.code
        }
        json_ = json.dumps(dic_)
        json_byte = bytes(json_, encoding="utf8")
        return [json_byte]


def ok_json_start_response():
    """
    返回函数计算常用返回参数200，json格式
    :return:
    """
    return '200 ok', [('Content-type', 'application/json')]


def ok_text_start_response():
    """
    返回函数计算常用返回参数200，text格式
    :return:
    """
    return '200 ok', [('Content-type', 'text/plain')]


def err_text_start_response():
    """
    返回函数计算常用返回参数500，text格式
    :return:
    """
    return '500 err', [('Content-type', 'text/plain')]


def err_json_start_response():
    """
    返回函数计算常用返回参数500，json格式
    :return:
    """
    return '500 err', [('Content-type', 'application/json')]


def ok_json_start_response_with_token(token: str):
    """
    返回函数计算常用返回参数200，json格式，包含token
    :return:
    """
    return '200 ok', [('Content-type', 'application/json'), ('E-Token', token),
                      ('Access-Control-Expose-Headers', 'E-Token'),
                      ('Access-Control-Allow-Headers',
                       'Origin, X-Requested-With, Content-Type, Accept, Connection, User-Agent, Cookie, E-Token')]


def err_json_start_response_with_token(token: str):
    """
    返回函数计算常用返回参数500，json格式，包含token
    :return:
    """
    return '500 err', [('Content-type', 'application/json'), ('E-Token', token),
                       ('Access-Control-Expose-Headers', 'E-Token'),
                       ('Access-Control-Allow-Headers',
                        'Origin, X-Requested-With, Content-Type, Accept, Connection, User-Agent, Cookie, E-Token')]

# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import csv
import re
import threading
from typing import Text, List, Set, Dict, Union, Tuple, Callable
from faker import Faker

fa = Faker('zh_CN')
_lock = threading.RLock()
app_functions = {}


def get_app_function(function_name: Text) -> Callable:
    global app_functions
    if not app_functions or len(app_functions) < 1:
        _lock.acquire()
        if not app_functions or len(app_functions) < 1:
            import melon
            app_functions = melon.loader.APPLICATION_FUNCTIONS
    return app_functions.get(function_name)


class CollUtil:

    @staticmethod
    def is_not_empty(coll: Union[List, Set, Tuple]) -> bool:
        return coll and len(coll) > 0

    @staticmethod
    def is_empty(coll: Union[List, Set, Tuple, Dict]) -> bool:
        return not CollUtil.is_not_empty(coll)


class StrUtil:

    @staticmethod
    def is_not_blank(string: Text) -> bool:
        return string and len(string.strip()) > 0

    @staticmethod
    def is_blank(string: Text) -> bool:
        return not StrUtil.is_not_blank(string)


class ParameterizeUtil:
    """
    参数化工具
    """

    @staticmethod
    def read_csv_dict(path: Text, headers=None) -> List[Dict]:
        """
        读取csv内容
        :param path: csv文件路径
        :param headers: 表头(为空则默认取首行为表头)
        """
        with open(file=path, encoding='UTF-8') as csv_file:
            contents = [ParameterizeUtil.__parse_expressions(line) for line in csv_file
                        if not line.startswith('#')]
            lines = list(csv.DictReader(contents, fieldnames=headers))
        return lines

    @staticmethod
    def read_csv(path: Text, ignore_first_line=True) -> List[List]:
        """
        读取csv内容
        :param path: csv文件路径
        :param ignore_first_line: 是否忽略首行
        """
        with open(path, encoding='utf8') as csv_file:
            contents = [ParameterizeUtil.__parse_expressions(line) for line in csv_file if not line.startswith('#')]
            reader = csv.reader(contents)
            lines = list(reader)
        if ignore_first_line:
            del lines[0]
        return lines

    @staticmethod
    def __parse_expressions(raw_str: Text):
        """
        解析所有表达式
        ${mock__function_name()} 调用 faker 中 mock 函数
        ${app__function_name()} 调用 application.py 中自定义函数

        :param raw_str: csv 行原字符串
        :return: 解析后数值
        """
        # 解析函数调用
        try:
            return ParameterizeUtil.__parse_function(raw_str)
        except Exception as e:
            raise ValueError(f'invalid expression [{e.args[0]}]')

    @staticmethod
    def __parse_function(expression: Text):
        """解析函数调用"""
        pattern = r'\${(mock|app)__(\w+?)\((.*?)\)}'
        matched_list = re.findall(pattern, expression)

        # 已匹配列表
        if not matched_list or len(matched_list) < 1:
            return expression

        # 替换解析后数值
        _format = '${%s__%s(%s)}'
        matched_list = [
            ParameterizeUtil.__function_call(
                items[0], items[1], items[2]
            ) or _format % items for items in matched_list
        ]

        expression = re.sub(pattern=pattern, repl="{}", string=expression)
        return expression.format(*matched_list)

    @staticmethod
    def __function_call(prefix: Text, function_name: Text, parameters: Text):
        """函数调用"""
        # 参数
        if StrUtil.is_blank(parameters):
            args = []
        else:
            args = [arg.strip() for arg in parameters.split(',')]

        try:
            if prefix == 'mock':
                return eval(f'fa.{function_name}({parameters})')
            elif prefix == 'app':
                app_function = get_app_function(function_name)
                return app_function(*args) if app_function else None
            else:
                return None
        except AttributeError:
            return None

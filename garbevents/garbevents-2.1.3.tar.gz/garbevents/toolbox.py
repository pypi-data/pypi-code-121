#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2022/3/22 5:45 下午
@Desc    :  toolbox line.
"""
import ast
import time
import datetime
import jmespath
import urllib.parse
import traceback

from airtest.core.api import log, assert_equal, device
from utx.core.utils.tools import str_to_bool
from deepdiff import DeepDiff
from loguru import logger


def diff(expect, actual, complete=True, exclude_paths=None) -> dict:
    """
    analysis diff result
    old new
    :param expect: expect
    :param actual: actual
    :param complete: match type, match complete or include, default complete.
    :param exclude_paths: parameter whitelist is empty by default.
    :return: {'result': True, 'data': {}}
    :Example:
        >>> {'result': True, 'data': {'dictionary_item_added': [root['data']]}}
    """
    exclude_paths = set([f"root['{path}']" for path in str(exclude_paths).split(',')])
    if len(exclude_paths) == 0:
        exclude_paths = None

    if not isinstance(expect, dict):
        expect = ast.literal_eval(expect)
    if not isinstance(actual, dict):
        actual = ast.literal_eval(actual)

    compare_results = DeepDiff(expect, actual, view='text', ignore_order=True,
                               exclude_paths=exclude_paths).to_dict()
    if not complete:
        if compare_results.get("values_changed"):
            result = False
        else:
            result = True
    else:
        if compare_results.get("dictionary_item_added") or compare_results.get(
                "dictionary_item_removed") or compare_results.get("values_changed") or compare_results.get(
            "iterable_item_added") or compare_results.get("iterable_item_removed"):
            result = False
        else:
            result = True

    return {'result': result, 'data': compare_results}


def extract(expressions, data):
    """
    extract the value you want！
    help documentation >>> https://jmespath.org/tutorial.html
    :param expressions: jsonpath expressions
    :param data: data dict
    :return: the value you want
    :Example:
        >>> test_dict = {"a": {"b": {"c": {"d": "value"}}}}
        >>> result = extract(expressions='a.b.c.d', data = test_dict)
        >>> print(result)
        >>> # value
    """
    _data = jmespath.search(expressions, data)
    return _data


def timestamp():
    """
    timestamp tool
    :return:
    """
    return int(round(time.time() * 1000))


def datetime_strife(fmt="%Y-%m-%d_%H-%M-%S"):
    """
    format datetime tool
    :param fmt: %Y-%m-%d_%H-%M-%S
    :return:
    """
    return datetime.datetime.now().strftime(fmt)


def sleep(seconds=1.0):
    """
    sleep time
    :param seconds:
    :return:
    """
    time.sleep(seconds)


def target(target_url, sign='stag=', index=1) -> dict:
    """
    the value you want！
    :param index: default 1
    :param sign: split flag
    :param target_url: encoded string
    :return: the value you want！
    """
    stag = ast.literal_eval(str(urllib.parse.unquote(target_url).split(sign)[index].split('&')[0]))

    return stag


def assert_diff(result: dict, equal: bool = True):
    """
    Assert two values are equal
    :param equal: verify True or False, default True
    :param result: toolbox.diff() return value
    :raise AssertionError: if assertion
    :return: None
    """
    # Report step
    log(arg=str(result['data']).replace('old_value', 'expect_value').replace('new_value', 'actual_value'),
        desc='Diff Details')

    # Assertion
    assert_equal(first=equal, second=result['result'], msg="Diff Result")


def search(start_time, end_time, api, types):
    """

    :param types: request or response
    :param start_time: 13-bit, millisecond timestamp, 1648545731537.
    :param end_time: default current timestamp, 1648645731537
    :param api: interface name.
    :return: interface information list.
    :Example:
        >>> search_data = search(start_time=1648545731537, end_time=1648645731537, api='/api/test', types='request')
        >>> print(search_data)
        >>> # [{'invokedBy': 'open'}]
    """
    from garbevents.db import proxy_data
    data_collection = proxy_data.query(
        f"select {types} from proxy where timestamps between {start_time} and {end_time} "
        f"and api == '{api}' and client_ip == '{device().get_ip_address()}';")

    res = []
    for data in data_collection:
        for d in data:
            res.append(ast.literal_eval(d))
    return res


def match(cases: list, sign='stag=', index=1, equal: bool = True):
    """

    :param cases:
    :param sign:
    :param index:
    :param equal:
    :raise AssertionError: if assertion
    :return: None
    """
    for info in cases:
        if not isinstance(info, dict):
            info = ast.literal_eval(info)
        try:
            excepts = info['excepts']

            search_data = search(start_time=info['search']['start_time'], end_time=info['search']['end_time'],
                                 api=info['api'], types=info['types'])
            detail = []
            for _data in search_data:

                actual = extract(expressions=info['extract'], data=_data)

                if str_to_bool(info['target']):
                    actual = target(target_url=actual, sign=sign, index=index)

                result = diff(expect=excepts, actual=actual, complete=str_to_bool(info['diff']['complete']),
                              exclude_paths=info['diff']['exclude_paths'])
                detail.append(result)

            if len(detail) > 1:
                flag = True
                for res in detail:
                    if res['result']:
                        assert_diff(result=res, equal=equal)
                        flag = False
                        break
                if flag:
                    log(arg=str(detail).replace('old_value', 'expect_value').replace('new_value', 'actual_value'),
                        desc='No Results Were Matched')
                    assert_equal(first=True, second=False, msg="Multiple Diff Result")
            else:
                try:
                    assert_diff(result=detail[0], equal=equal)
                except IndexError:
                    logger.error(traceback.format_exc())
        except AssertionError:
            logger.error(traceback.format_exc())
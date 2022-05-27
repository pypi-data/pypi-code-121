# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.utils.logger_utils import LoggerUtils
import json
import requests
import sys
import traceback


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)

class HttpRequest:
    @staticmethod
    def post_json(url, data):
        """
        :param url:
        :param data: dict like
        :return:
        """
        headers = {'Content-type': 'application/json; charset=utf-8'}
        r = requests.post(url, json=data, headers=headers)
        try:
            response = json.loads(r.text)
            if 'success' not in response or not response['success']:
                LoggerUtils().get_logger().error('[Intraday] post signals not success')
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            LoggerUtils().get_logger().error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            LoggerUtils().get_logger().error('[Intraday] post error')
        return

    @staticmethod
    def get_json(resp):
        resp.headers['Content-type'] = 'application/json;charset=utf-8'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
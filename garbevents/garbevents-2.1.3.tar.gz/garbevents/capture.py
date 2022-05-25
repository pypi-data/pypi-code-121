#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2022/3/21 10:35 上午
@Desc    :  caSTure line.
"""
import json
import mitmproxy
from mitmproxy import http
from loguru import logger

from garbevents.db import proxy_data
from garbevents.settings import Settings as ST
from garbevents.toolbox import timestamp


class GetData:
    """
    A garbevents HTTP engine class.
    """

    def __init__(self):
        self.sql = proxy_data
        self.sql.execute(
            "CREATE TABLE IF NOT EXISTS proxy(id INTEGER PRIMARY KEY AUTOINCREMENT,timestamps,api,request,response,client_ip);")

    def response(self, flow: mitmproxy.http.HTTPFlow):
        """
        Proxy service data analysis
        :param flow:
        :return:
        """

        if ST.url in flow.request.url:

            client_ip = flow.client_conn.peername[0]
            logger.info("Get client IP address after splitting ====>"
                        "{}".format(client_ip))
            api = flow.request.path.split('?')[0]
            logger.info("Get API address after splitting ====>"
                        "{}".format(api))
            try:
                request_content = json.loads(flow.request.get_text())
            except Exception as e:
                logger.error(e)
                request_content = {}
            logger.info("Get request content after splitting ====>"
                        "{}".format(request_content))
            try:
                response_content = json.loads(flow.response.text)
            except Exception as e:
                logger.error(e)
                response_content = {}
            logger.info("Get response content after splitting ====>"
                        "{}".format(response_content))
            self.sql.execute("INSERT INTO proxy values(NULL,?,?,?,?,?)",
                             (timestamp(), api, str(request_content), str(response_content), str(client_ip)))

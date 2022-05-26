# -*- coding: utf-8 -*-
# @Time: : 2022/5/26 15:14
# @File: parser.py
# @Author : Cooper
# @Software: PyCharm

class SurlParser:
    """http/https url解析"""

    def __init__(self):
        # 协议 端口 域名 路径 请求参数 默认值为None
        self.protocol = None
        self.port = None
        self.domain = None
        self.path = None
        self.params = None

    def parser(self, url: str):
        """url解析"""
        url_temp = url
        if "://" in url_temp:
            self.protocol, url_temp = url.split("://")
            if not self.protocol or self.protocol not in ["http", "https"]:
                raise TypeError(f"当前仅支持http, https协议url数据的解析, 当前数据类型为: {self.protocol}")

        if "/" in url_temp:
            proto_port = url_temp.split("/")[0]
            if ":" in proto_port:
                self.domain = proto_port.split(":")[0]
                self.port = int(proto_port.split(":")[1])if proto_port.split(":")[1].isdigit() else None
            else:
                self.domain = proto_port
                self.port = 443 if self.protocol == "https" else 80
            url_path = "/".join(url_temp.split("/")[1:])
            if "?" in url_path:
                self.path = f'/{url_path.split("?")[0]}'
                self.params = "?".join(url_path.split("?")[1:])
            else:
                self.path = f'/{url_path}'
        else:
            if ":" in url_temp:
                self.domain = url_temp.split(":")[0]
                self.port = int(url_temp.split(":")[1])if url_temp.split(":")[1].isdigit() else None
            else:
                self.domain = url_temp

        if "://" not in url and ":" not in url and "/" not in url:
            self.domain = url

    @property
    def dict(self) -> dict:
        return self.__dict__

# -*- coding: utf-8 -*-
# author QXC NWU
# TIME 2022/4/13

import json
import ssl
from typing import List
from urllib.request import urlopen, Request

import pandas as pd
import requests
from ModisDownload.Base import Base, Sensors


class Login:
    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password
        self._login_url = "http://36.112.130.153:7777/manage/uaa/loginToken"
        self._data = {
            "username": self._username,
            "password": self._password
        }
        self.login_ans = None
        self._login()
        self.loginflag = self.login_ans is not None and str(self.login_ans["status"]) == "200"
        if self.loginflag: print("登陆成功")

    def _login(self):
        def encode():
            _json = json.dumps(self._data)
            _json = _json.replace("\n", "")
            return _json.encode("utf-8")

        jsonBytes = encode()
        try:
            print("正在登录")
            fh = requests.post(self._login_url, data=self._data, headers=self.get_header(len(jsonBytes)), verify=False)
            self.login_ans = json.loads(fh.content.decode("utf-8"))
        except Exception as ex:
            print("登陆失败:", ex)
        return

    @staticmethod
    def get_header(length: int):
        return {
            "Host": "36.112.130.153:7777",
            "Connection": "keep-alive",
            "Content-Length": str(length),
            "Accept": "application/json,text/plain,*/*",
            "DNT": "1",
            "access-agent": "pc-dss",
            "murmur": "96caaa0f25088aaa1f35de3c8dc73814",
            "User-Agent": "Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/101.0.4951.64Safari/537.36Edg/101.0.1210.53",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http//36.112.130.153:7777",
            "Referer": "http://36.112.130.153:7777/",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "loginFlag=1"
        }


class SearchData(Base):
    def __init__(self, startdate: str, enddate: str, sensors: List[Sensors], position: List[str], cloud: int,
                 productlev: int, login: Login = None):
        """
        组装多个不同的传感器，地理位置
        """
        super().__init__()
        self.jsonlist = []
        self.startdate = startdate
        self.enddate = enddate
        self.sensors = sensors
        self.position = position
        self.cloud = cloud
        self.productlev = productlev
        self.type_lists = {"gx": [], "ld": [], "dq": [], "dc": [], "jg": []}
        self.login = login
        self._make_json()

    def _make_json(self):
        for i in self.sensors:
            temp_sensors = self.type.get(i.name)
            for j in self.position:
                if self.login is not None and self.login.loginflag:
                    self.jsonlist.append({
                        "page": 1,
                        "size": 200 * 365,
                        "geom": [j],
                        "scenetime": [
                            self.startdate,
                            self.enddate
                        ],
                        "satelliteSensor": [i.name],
                        "prodlevel": self.productlev,
                        "cloudpsd": self.cloud,
                        "dwxtype": temp_sensors,
                        "userIndustry": self.login.login_ans["data"].get("industry"),
                        "userType": self.login.login_ans["data"].get("usertype"),
                        "userId": self.login.login_ans["data"].get("userid"),
                        "crossed": "false",
                        "desc": [
                            "scenetime"
                        ]
                    })
                else:
                    self.jsonlist.append({
                        "page": 1,
                        "size": 200 * 365,
                        "geom": [j],
                        "scenetime": [
                            self.startdate,
                            self.enddate
                        ],
                        "satelliteSensor": [i.name],
                        "prodlevel": self.productlev,
                        "cloudpsd": self.cloud,
                        "dwxtype": temp_sensors,
                        "userType": "0",
                        "userId": self._get_ip(),
                        "crossed": "False",
                        "desc": [
                            "scenetime"
                        ]
                    })
        return


class SearchChina(Base):
    def __init__(self, searchData: SearchData, show_proc=False):
        """
        查询产品类
        Args:
            searchData:查询对象
            show_proc:显示结果
        """
        super().__init__()

        # check sensors in sensors list
        self.show_proc = show_proc
        self._json = searchData.jsonlist
        self.answer = None
        self.dict = None
        self.result = []
        self.header = None
        self.pdfram = None
        if searchData.login is not None:
            self.loginFlag = searchData.login.loginflag
            self.auth = searchData.login.login_ans["data"].get("token")
            self.username = searchData.login.login_ans["data"].get("username")
        else:
            self.loginFlag = False

    def search(self):
        for i in self._json:
            self._upload(i)
        return

    def _choseheader(self, length):
        if not self.loginFlag:
            return self._get_header(length)
        else:
            return self._getLoginheader(length, self.auth, self.username)

    def _upload(self, js):
        """
        查询
        Returns: None
        """

        def encode():
            _json = json.dumps(js)
            _json = _json.replace("\n", "")
            return _json.encode("utf-8")

        jsonBytes = encode()
        CTX = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        try:
            # print("正在查询")
            fh = urlopen(Request(self.url, headers=self._choseheader(len(jsonBytes)), data=jsonBytes), context=CTX)
            self.answer = fh.read()
            self._parse()
            # print("查询成功")
        except Exception as e:
            print(js["satelliteSensor"], "没有权限")
        return

    def _parse(self):
        self.dict = json.loads(self.answer)
        if self.dict is None:
            print("未查询到任何产品")
            return
        if int(self.dict["size"]) == 0:
            print("未查询到任何产品")
            return
        self.header = [i for i in self.dict["result"][0].keys()]
        for item in self.dict["result"]:
            self.result.append([i for i in item.values()])
        self.pdfram = pd.DataFrame(self.result, columns=self.header)
        if self.show_proc:
            self._show()
        return

    def _show(self):
        print(self.header)
        for i in self.result:
            print(i)
        return

    def save_ans(self, save_path):
        """
        保存查询结果
        Args:
            save_path: 保存路径
        Returns:
        """
        if self.pdfram is None:
            print("未查询到任何结果")
            return
        self.pdfram.to_csv(save_path, index=None)
        return

    def get_size(self):
        """
        获取结果集大小
        Returns:

        """
        return self.dict["size"]

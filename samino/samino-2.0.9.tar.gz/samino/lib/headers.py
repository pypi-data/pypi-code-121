import json
import random
import string
from .util import c, s, uu

uid = None
sid = None
deviceId = None
lang = None


class Headers:
    def __init__(self, data=None):
        if deviceId: self.deviceId = deviceId
        else: self.deviceId = c()

        self.headers = {
            "NDCDEVICEID": self.deviceId,
            "AUID": uu(),
            "SMDEVICEID": uu(),
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-N975F Build/samsung-user 7.1.2 2; com.narvii.amino.master/3.4.33602)",
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Upgrade"
        }
        self.web_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ar,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            "x-requested-with": "xmlhttprequest"
        }

        if sid:
            self.headers["NDCAUTH"] = sid
            self.web_headers["cookie"] = sid

        if uid:
            self.uid = uid

        if data:
            self.headers["Content-Length"] = str(len(data))
            if type(data) is not str: data = json.dumps(data)
            self.headers["NDC-MSG-SIG"] = s(data)

        if lang:
            self.headers.update({"NDCLANG": lang[:lang.index("-")], "Accept-Language": lang})

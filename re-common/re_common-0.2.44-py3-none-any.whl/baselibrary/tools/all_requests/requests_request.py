import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from re_common.baselibrary.tools.all_requests.mrequest import MRequest
from re_common.baselibrary.utils.baseurl import BaseUrl
from re_common.baselibrary.utils.core.mdeprecated import request_try_except

from re_common.baselibrary.utils.core.requests_core import set_proxy

disable_warnings(InsecureRequestWarning)


class RequestsRequest(MRequest):

    def __init__(self, logger=None):
        if logger is None:
            from re_common.baselibrary import MLogger
            logger = MLogger().streamlogger
        super().__init__(logger=logger)
        self.kwargs = {}

    def builder(self):
        if self.refer:
            self.header["refer"] = self.refer
        self.kwargs["headers"] = self.header
        self.kwargs["proxies"] = set_proxy(self.proxy)
        if BaseUrl.urlScheme(self.url) == "https":
            self.kwargs["verify"] = False
        self.kwargs["timeout"] = self.timeout
        self.kwargs["allow_redirects"] = self.allow_redirects
        self.kwargs["params"] = self.params
        return self

    @request_try_except
    def get(self):
        if self.sn:
            r = self.sn.get(url=self.url, **self.kwargs)
        else:
            r = requests.get(url=self.url, **self.kwargs)

        self.resp = r
        self.set_status_code(r.status_code)
        r.encoding = r.apparent_encoding
        self.html = r.text.strip()
        return True, {"code": self.status_code, "msg": ""}

    @request_try_except
    def post(self):
        if self.sn:
            r = self.sn.post(url=self.url, data=self.data, **self.kwargs)
        else:
            r = requests.post(url=self.url, data=self.data, **self.kwargs)

        self.resp = r
        self.set_status_code(r.status_code)
        r.encoding = r.apparent_encoding
        self.html = r.text.strip()
        return True, {"code": self.status_code, "msg": ""}

    def all_middlerwares(self):
        bools, dicts = True, {}
        for item in self.middler_list:
            bools, dicts = item()
            if not bools:
                return bools, dicts
        return bools, dicts

    def run(self, moths="get"):
        self.builder()
        self.on_request_start()
        if moths == MRequest.GET:
            bools, dicts = self.get()
        elif moths == MRequest.POST:
            bools, dicts = self.post()
        else:
            bools, dicts = False, {}
        self.on_request_end()
        if bools:
            return self.all_middlerwares()
        return bools, dicts

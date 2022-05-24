import aiohttp
import httpx
from re_common.baselibrary.tools.all_requests.mrequest import MRequest
from re_common.baselibrary.utils.baseurl import BaseUrl
from re_common.baselibrary.utils.core.mdeprecated import aiohttp_try_except
from re_common.baselibrary.utils.core.mlamada import html_strip
from re_common.baselibrary.utils.core.requests_core import set_proxy_aio, set_proxy_httpx


async def default_resp_hook(self, resp):
    pass


class HttpxRequest(MRequest):

    def __init__(self, logger=None):
        if logger is None:
            from re_common.baselibrary import MLogger
            logger = MLogger().streamlogger
        super().__init__(logger=logger)
        self.kwargs = {}
        self.client_session_kwargs = {}
        self.resp_hook = default_resp_hook
        # 预留一个字典可以向里面传入其他信息
        self.other_dicts = {}

    def set_resp_hook(self, resp_hook_func):
        self.resp_hook = resp_hook_func
        return self

    def builder(self):
        self.kwargs["params"] = self.params
        if self.refer:
            self.header["refer"] = self.refer
        self.kwargs["headers"] = self.header
        self.kwargs["cookies"] = self.cookies
        self.kwargs["follow_redirects"] = self.allow_redirects
        self.kwargs["timeout"] = self.timeout
        if self.proxy:
            self.client_session_kwargs["proxies"] = set_proxy_httpx(self.proxy)
        if BaseUrl.urlScheme(self.url) == "https":
            self.client_session_kwargs["verify"] = False
        return self

    def set_resp(self, resp):
        self.resp = resp
        self.set_status_code(resp.status_code)
        # 有时候302时我们去获取html会报错
        if self.allow_resp_text:
            if self.resp_encoding:
                resp.encoding = self.resp_encoding
            self.html = resp.text
            self.html = html_strip(self.html)
        else:
            self.html = None
        if self.allow_resp_bytes:
            self.html_bytes = resp.content
        else:
            self.html_bytes = None

    @aiohttp_try_except
    async def get(self):
        if self.sn is None:
            # skip_auto_headers 用法: 不对列表内的对应参数进行自动生成
            self.sn = httpx.AsyncClient(**self.client_session_kwargs)
        async with self.sn:
            resp = await self.sn.get(url=self.url, **self.kwargs)
            self.set_resp(resp)
            await self.resp_hook(self, resp)
        return True, {"code": self.status_code, "msg": ""}

    @aiohttp_try_except
    async def post(self):
        if self.sn is None:
            self.sn = httpx.AsyncClient(**self.client_session_kwargs)
        async with self.sn:
            resp = await self.sn.post(url=self.url, data=self.data, **self.kwargs)
            self.set_resp(resp)
            await self.resp_hook(self, resp)
        return True, {"code": self.status_code, "msg": ""}

    def all_middlerwares(self, dicts):
        bools = True
        for item in self.middler_list:
            bools, dicts = item()
            if not bools:
                return bools, dicts
        return bools, dicts

    async def run(self, moths="get"):
        self.builder()
        self.on_request_start()
        if moths == MRequest.GET:
            bools, dicts = await self.get()
        elif moths == MRequest.POST:
            bools, dicts = await self.post()
        else:
            bools, dicts = False, {}
        self.on_request_end()
        if bools:
            return self.all_middlerwares(dicts)
        return bools, dicts

import aiohttp
from aiohttp_socks import ProxyConnector
from re_common.baselibrary.tools.all_requests.mrequest import MRequest
from re_common.baselibrary.utils.baseurl import BaseUrl
from re_common.baselibrary.utils.core.mdeprecated import aiohttp_try_except
from re_common.baselibrary.utils.core.mlamada import html_strip
from re_common.baselibrary.utils.core.requests_core import set_proxy_aio


async def default_resp_hook(self, resp):
    pass


class AioHttpRequest(MRequest):

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
        if self.refer:
            self.header["refer"] = self.refer
        self.kwargs["headers"] = self.header
        # 比如在请求之前调用API请求COOKIE,这时这个调用就没得 代理
        self.client_session_kwargs["skip_auto_headers"] = self.skip_auto_headers
        if self.proxy:
            if "socks" in self.proxy:
                if self.force_close == "true":
                    connector = ProxyConnector.from_url(self.proxy, force_close=True)
                else:
                    connector = ProxyConnector.from_url(self.proxy)
                self.client_session_kwargs["connector"] = connector
                self.sn = aiohttp.ClientSession(**self.client_session_kwargs)
            else:
                self.kwargs["proxy"] = set_proxy_aio(self.proxy)
        else:
            self.kwargs["proxy"] = set_proxy_aio(self.proxy)
        if self.force_close == "true" and "connector" not in self.client_session_kwargs.keys():
            connector = aiohttp.TCPConnector(force_close=True)
            self.client_session_kwargs["connector"] = connector
        if BaseUrl.urlScheme(self.url) == "https":
            self.kwargs["verify_ssl"] = False
        self.kwargs["timeout"] = self.timeout
        self.kwargs["allow_redirects"] = self.allow_redirects
        self.kwargs["params"] = self.params
        self.kwargs["cookies"] = self.cookies
        return self

    async def set_resp(self, resp):
        self.resp = resp
        self.set_status_code(resp.status)
        # 有时候302时我们去获取html会报错
        if self.allow_resp_text:
            if self.resp_encoding is not None:
                self.html = await resp.text(encoding=self.resp_encoding, errors=self.resp_errors)
            else:
                self.html = await resp.text(errors=self.resp_errors)
            self.html = html_strip(self.html)
        else:
            self.html = None
        if self.allow_resp_bytes:
            self.html_bytes = await resp.content.read()
        else:
            self.html_bytes = None

    @aiohttp_try_except
    async def get(self):
        if self.sn is None:
            # skip_auto_headers 用法: 不对列表内的对应参数进行自动生成
            self.sn = aiohttp.ClientSession(**self.client_session_kwargs)
        async with self.sn:
            async with self.sn.get(url=self.url, **self.kwargs) as resp:
                await self.set_resp(resp)
                await self.resp_hook(self, resp)
        return True, {"code": self.status_code, "msg": ""}

    @aiohttp_try_except
    async def post(self):
        if self.sn is None:
            self.sn = aiohttp.ClientSession(**self.client_session_kwargs)
        async with self.sn:
            async with self.sn.post(url=self.url, data=self.data, **self.kwargs) as resp:
                await self.set_resp(resp)
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

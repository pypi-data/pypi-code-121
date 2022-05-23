try:
    import aiohttp
except ImportError:
    raise ImportError("이 커넥터는 호출할 수 없습니다. 패키지를 설치해주세요.")

from typing import Optional, Dict
from http.cookies import SimpleCookie
from concurrent.futures._base import TimeoutError as _TimeoutError

from .base import (
    BaseRequest,
    Response,
    HTTPRequestMethod,
    BodyFormatter,
    DEFAULT_REQUEST_TIMEOUT,
)
from ..exceptions import RequestTimeoutError


class Request(BaseRequest):
    @classmethod
    async def _request(
        cls,
        method: HTTPRequestMethod,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, str]] = None,
        body_encoding: BodyFormatter = BodyFormatter.URL_ENCODE,
        cookies: Dict[str, str] = None,
        verify: bool = True,
        allow_redirects: bool = False,
        timeout: Optional[float] = None,
        proxies: Optional[str] = None,
    ) -> Response:
        timeout = timeout or DEFAULT_REQUEST_TIMEOUT
        if proxies is not None:
            from aiohttp_socks import ProxyConnector

            proxies = ProxyConnector.from_url(proxies)
        async with aiohttp.ClientSession(connector=proxies) as session:
            try:
                async with session.request(
                    method.value,
                    url,
                    headers=headers,
                    cookies=cls._to_cookie_obj(cookies),
                    verify_ssl=verify,
                    allow_redirects=allow_redirects,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    **{body_encoding.value: body},
                ) as response:
                    cookies = cls._to_cookie_dict(response.cookies)
                    headers = dict(response.headers)
                    raw = await response.read()
                    try:
                        text = await response.text()
                    except UnicodeDecodeError:
                        text = ""

                    return Response(
                        response.status,
                        url,
                        response.reason,
                        headers,
                        raw,
                        text,
                        cookies,
                    )
            except _TimeoutError as e:
                raise RequestTimeoutError(f"요청시간이 경과하였습니다. -> {timeout}초") from e

    @staticmethod
    def _to_cookie_obj(cookies: Dict[str, str]) -> SimpleCookie:
        return SimpleCookie(cookies)

    @staticmethod
    def _to_cookie_dict(cookie: SimpleCookie) -> Dict[str, str]:
        return {morsel.key: morsel.value for morsel in cookie.values()}

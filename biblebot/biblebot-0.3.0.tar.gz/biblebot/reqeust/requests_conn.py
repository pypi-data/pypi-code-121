try:
    import requests
except ImportError:
    raise ImportError("이 커넥터는 호출할 수 없습니다. 패키지를 설치해주세요.")

from typing import Optional, Dict
from functools import partial
import asyncio

import urllib3

from .base import (
    BaseRequest,
    Response,
    HTTPRequestMethod,
    BodyFormatter,
    DEFAULT_REQUEST_TIMEOUT,
)
from ..exceptions import RequestTimeoutError


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        proxies = None if proxies is None else {"http": proxies, "https": proxies}
        try:
            response: requests.models.Response = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(
                    requests.request,
                    method.value,
                    url,
                    headers=headers,
                    cookies=cookies,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    timeout=timeout,
                    proxies=proxies,
                    **{body_encoding.value: body},
                ),
            )
        except requests.exceptions.ConnectTimeout as e:
            raise RequestTimeoutError(f"요청시간이 경과하였습니다. -> {timeout}초") from e
        try:
            cookies = response.cookies.get_dict()
            return Response(
                response.status_code,
                url,
                response.reason,
                response.headers,
                response.content,
                response.text,
                cookies,
            )
        finally:
            response.close()

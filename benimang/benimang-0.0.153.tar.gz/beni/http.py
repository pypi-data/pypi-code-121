import asyncio
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, build_opener, install_opener

import aiofiles
import aiohttp

import beni
import beni.lock as block

_limit: Final = 5
_defaultRetry = 3

_httpHeaders = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}


def _makeHttpHeaders(headers: dict[str, Any] | None = None):
    if headers:
        return _httpHeaders | headers
    else:
        return dict(_httpHeaders)


@block.limit(_limit)
async def get(
    url: str,
    *,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int | None = None,
):
    retry = retry or _defaultRetry
    while True:
        retry -= 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=_makeHttpHeaders(headers), timeout=timeout) as response:
                    result = await response.read()
                    if not result:
                        await asyncio.sleep(0.5)
                        raise Exception('http get result is empty')
                    return result, response
        except:
            if retry <= 0:
                raise


async def getContent(
    url: str,
    *,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int | None = None,
):
    resultBytes, _ = await get(
        url,
        headers=headers,
        timeout=timeout,
        retry=retry,
    )
    return resultBytes.decode()


@block.limit(_limit)
async def post(
    url: str,
    *,
    data: bytes | dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int | None = None,
):
    retry = retry or _defaultRetry
    while True:
        retry -= 1
        try:
            postData = data
            if type(data) is dict:
                postData = urlencode(data).encode()
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=postData, headers=_makeHttpHeaders(headers), timeout=timeout) as response:
                    result = await response.read()
                    if not result:
                        await asyncio.sleep(0.5)
                        raise Exception('http get result is empty')
                    return result, response
        except:
            if retry <= 0:
                raise


@block.limit(_limit)
async def download(url: str, file: Path, timeout: int = 300):
    total_size: int = 0
    download_size: int = 0
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=_httpHeaders, timeout=timeout) as response:
                beni.makeDir(file.parent)
                assert response.content_length, '下载内容为空'
                total_size = response.content_length
                async with aiofiles.open(file, 'wb') as f:
                    while True:
                        data = await response.content.read(1024 * 1024)
                        if data:
                            await f.write(data)
                            download_size += len(data)
                        else:
                            break
        assert total_size and total_size == download_size, '下载为文件不完整'
    except:
        beni.remove(file)
        raise


def setDefaultRetry(value: int):
    global _defaultRetry
    _defaultRetry = value


# Cookie
_cookie = CookieJar()
_cookieProc = HTTPCookieProcessor(_cookie)
_opener = build_opener(_cookieProc)
install_opener(_opener)

# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests


def async_get(url_list, max_cpu=None, max_request_per_cpu=None, callback_func=None):
    async def get_response_content(url, session):
        async with session.get(url) as response:
            return await response.read()

    async def bound_fetch(sem, url, session, callback):
        # Getter function with semaphore.
        async with sem:
            content = await get_response_content(url, session)
            callback(url, content)
            return

    async def run(_url_list, sem):
        tasks = []

        # Create client session that will ensure we dont open new connection
        # per each request.
        async with aiohttp.ClientSession() as session:
            for url in _url_list:
                task = asyncio.ensure_future(bound_fetch(sem, url, session, callback_func))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        run(
            url_list,
            sem=asyncio.Semaphore(max_request_per_cpu if max_request_per_cpu > len(url_list) else len(url_list))
        ))
    loop.run_until_complete(future)


def async_request_get(url_list, time_out=None, proxy=None, sema_count=None, response_callback=None):
    """

    :rtype: list of str|Exception|bytes
    :type response_callback: None|callable
    :type sema_count: None|int
    :type proxy: Nont|str
    :type time_out: None|int
    :type url_list: list of str
    """

    def sorted_response(response_list):
        return [data for (index, data) in sorted(response_list, key=lambda index_data: index_data[0])]

    if sema_count and sema_count > len(url_list):
        sema_count = len(url_list)

    # aiohttp only support http
    if proxy is None or proxy.startswith("http://"):
        async def get_async(url, index):
            if time_out is None:
                try:
                    async with aiohttp.request('GET', url, proxy=proxy, ) as r:
                        data = await r.read()
                        if response_callback:
                            data = response_callback(data)
                    return index, data
                except Exception as e:
                    return index, e
            else:
                timeout = aiohttp.ClientTimeout(total=time_out)
                try:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(url, timeout=timeout, proxy=proxy) as r:
                            data = await r.read()
                            if response_callback:
                                data = response_callback(data)
                    return index, data
                except Exception as e:
                    return index, e

        if sema_count is None:
            # not use sema
            event_loop = asyncio.get_event_loop()
            tasks = [get_async(url, index) for index, url in enumerate(url_list)]
            results = event_loop.run_until_complete(asyncio.gather(*tasks))
            return sorted_response(results)

        # use sema
        sema = asyncio.Semaphore(sema_count)
        result_list = []

        async def dealwith_result(url, index):
            with (await sema):
                index, data = await get_async(url, index)
                result_list.append((index, data))

        loop = asyncio.get_event_loop()
        f = asyncio.wait([dealwith_result(url, index) for index, url in enumerate(url_list)])
        loop.run_until_complete(f)

        return sorted_response(result_list)

    else:
        # threadpool + requests
        def get_block(url_index):
            url, index = url_index
            try:
                data = requests.get(
                    url,
                    timeout=time_out,
                    proxies={'http': proxy, 'https': proxy} if proxy else None
                ).content
                if response_callback:
                    data = response_callback(data)
                return index, data
            except Exception as e:
                return index, e

        with ThreadPoolExecutor(max_workers=sema_count) as executor:
            result_list = [(index, data) for index, data in
                           executor.map(get_block, ((url, index) for index, url in enumerate(url_list)))]

        return sorted_response(result_list)


__all__ = ("async_request_get", "async_get")

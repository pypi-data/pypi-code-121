# Small python script to check the status of a list of urls.
# Copyright © 2022 Arthurdw
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,

"""Small python script to check the status of a list of urls.

Parameters:
    -u, --url: url to check
    -f, --file: file containing urls to check
    -t, --timeout: timeout in seconds
    -s, --secure: Try to use HTTPS instead of HTTP
    -h, --help: show this help message

Usage:
    # Single url
    statusof.py -u example.com
    statusof.py -u example.com -t 10

    # Multiple urls
    statusof.py -f urls.txt
    statusof.py -u example.com -u example2.com

Written with love by @Arthurdw (github.com/arthurdw)"""
from __future__ import annotations

import asyncio
import re
import sys
import getopt
from typing import Match, Optional
from aiohttp.client import ClientSession, ClientTimeout

from aiohttp.client_reqrep import ClientResponse
from aiohttp import ClientConnectionError

try:
    from colorama import init, Fore, Style
except ImportError:
    print(
        "Please install colorama to use this script."
        "This can be done using `pip install colorama`"
    )
    sys.exit(2)

PROTOCOL_REGEX = r"([a-z]{3,6}:\/\/|^|\s)"
CONTENT_REGEX = r"([a-zA-Z0-9\-]+\.+[a-z]{2,13})"
SUFFIX_REGEX = r"([\.\?\=\&\%\/\w\-]*\b([^@]|$))"

URL_MATCH = PROTOCOL_REGEX + CONTENT_REGEX + SUFFIX_REGEX

summary = {
    "total_urls": 0,
    "success": 0,
    "failure": 0,
    "server_failure": 0,
    "timeout": 0,
}

timeout = 10
secure = False


class Styles:
    TIMEOUT = Style.BRIGHT + Fore.LIGHTRED_EX
    URL_PREFIX = Style.NORMAL + Fore.LIGHTBLACK_EX
    URL_CONTENT = Style.BRIGHT + Fore.LIGHTBLUE_EX
    URL_SUFFIX = Style.DIM + Fore.LIGHTBLUE_EX
    URL_SUCCESS = Style.BRIGHT + Fore.LIGHTGREEN_EX
    URL_FAILURE = Style.BRIGHT + Fore.RED
    URL_SERVER_FAILURE = Style.BRIGHT + Fore.LIGHTMAGENTA_EX

    SUMMARY = Style.BRIGHT + Fore.LIGHTYELLOW_EX
    SUMMARY_TOTAL_URLS = Style.BRIGHT + Fore.CYAN
    SUMMARY_SUCCESS = Style.BRIGHT + Fore.GREEN
    SUMMARY_FAILURE = Style.BRIGHT + Fore.RED
    SUMMARY_TIMEOUT = Style.BRIGHT + Fore.LIGHTRED_EX
    SUMMARY_SERVER = Style.BRIGHT + Fore.LIGHTMAGENTA_EX


class ConnectionHandler:
    def __init__(self, url: str, wait_for: int):
        self.url = url
        timeout = ClientTimeout(total=wait_for)
        self.__session = ClientSession(timeout=timeout)

    async def __aenter__(self) -> ConnectionHandler:
        return self

    async def __aexit__(self, *_) -> None:
        await self.disconnect()

    async def disconnect(self) -> None:
        await self.__session.close()

    async def get(self) -> ClientResponse:
        async with self.__session.get(self.url) as response:
            return response


def get_url_args(url: str) -> Optional[Match[str]]:
    return re.search(URL_MATCH, url)


async def get_status(url: str):
    global timeout

    async with ConnectionHandler(url, timeout) as conn:
        res: ClientResponse = await conn.get()
        return res.status


async def display_status(url: str):
    groups = get_url_args(url)
    formatted_url = url

    if groups is not None:
        formatted_url = Styles.URL_PREFIX + groups.group(1)
        formatted_url += Styles.URL_CONTENT + groups.group(2)
        formatted_url += Styles.URL_SUFFIX + groups.group(3)
        formatted_url += Style.RESET_ALL

    summary["total_urls"] += 1

    try:
        status = await get_status(url)

        if status < 300 and status >= 200:
            status = Styles.URL_SUCCESS + str(status) + Style.RESET_ALL
            summary["success"] += 1
        elif status < 500 and status >= 400:
            status = Styles.URL_FAILURE + str(status) + Style.RESET_ALL
            summary["failure"] += 1
        elif status >= 500:
            status = Styles.URL_SERVER_FAILURE + str(status) + Style.RESET_ALL
            summary["server_failure"] += 1

        print(f"{status}: {formatted_url}")
    except ClientConnectionError as e:
        print(f"{e}: {formatted_url}")
        summary["failure"] += 1
    except asyncio.exceptions.TimeoutError:
        print(f"{Styles.TIMEOUT}Timeout{Style.RESET_ALL}: {formatted_url}")
        summary["timeout"] += 1


async def coro_main(urls: list[str] | str):
    init()
    if isinstance(urls, str):
        urls = [urls]

    coroutines = map(display_status, urls)
    await asyncio.gather(*coroutines)

    summary_text = Styles.SUMMARY + "Summary"
    total_urls = Styles.SUMMARY_TOTAL_URLS + str(summary["total_urls"])
    success = Styles.SUMMARY_SUCCESS + str(summary["success"])
    failure = Styles.SUMMARY_FAILURE + str(summary["failure"])
    server_failure = Styles.SUMMARY_SERVER + str(summary["server_failure"])
    timeout = Styles.SUMMARY_TIMEOUT + str(summary["timeout"])
    print(
        f"\n{summary_text}:",
        f"urls {total_urls}",
        f"success: {success}",
        f"failed: {failure}",
        f"server failure: {server_failure}",
        f"timeout: {timeout}",
        "",
        sep=f" {Style.RESET_ALL}",
    )


def get_valid_url(url: str) -> tuple[bool, Optional[str]]:
    res = get_url_args(url)

    if res is None:
        return False, None

    if not res.group(1):
        url = f"http{'s' if secure else ''}://" + url

    return True, url


def main():
    try:
        args = sys.argv[1:]

        if len(args) < 1:
            raise RuntimeError("Invalid arguments")

        full_commands = ["help=" "secure=", "url=", "file=", "timeout="]
        opts, _ = getopt.getopt(args, "shu:f:t:", full_commands)
    except (getopt.GetoptError, RuntimeError):
        print("Invalid arguments, use --help for help")
        sys.exit(2)

    urls: list[str] = []

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(__doc__)
            sys.exit()
        elif opt in ("-u", "--url"):
            urls.append(arg)
        elif opt in ("-f", "--file"):
            with open(arg, "r") as f:
                urls.extend(f.readlines())
        elif opt in ("-s", "--secure"):
            global secure
            secure = True
        elif opt in ("-t", "--timeout"):
            global timeout

            try:
                timeout = int(arg)
            except ValueError:
                print("Invalid timeout value")
                sys.exit(2)

    if len(urls) < 1:
        print("Invalid arguments, use --help for help")
        sys.exit(1)

    contains_invalid_url = False

    for idx, url in enumerate(urls):
        url = url.strip()
        is_valid, updated = get_valid_url(url)

        if not is_valid:
            print(f"Invalid url at position {idx + 1}: {repr(url)}")
            contains_invalid_url = True
            continue

        if updated:
            urls[idx] = updated

    if contains_invalid_url:
        print("Execution cancelled because of invalid url(s)")
        sys.exit(1)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    loop.run_until_complete(coro_main(urls))

    try:
        for task in asyncio.all_tasks(loop):
            if not (task.done() or task.cancelled()):
                loop.run_until_complete(task)
            else:
                task.cancel()
    finally:
        loop.stop()


if __name__ == "__main__":
    main()

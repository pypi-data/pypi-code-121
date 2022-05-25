#!/usr/bin/env python
# coding=utf-8

"""
Version: 0.1
Autor: zmf96
Email: zmf96@qq.com
Date: 2022-02-24 08:26:18
LastEditors: zmf96
LastEditTime: 2022-03-30 19:02:35
FilePath: /hotfinger/__main__.py
Description: 
"""
import argparse
import json

from loguru import logger

from hotfinger import ErrFingers, async_run, init

if __name__ == "__main__":
    logger.debug("hotfinger  version 0.1")
    parser = argparse.ArgumentParser(description="hotfinger v0.1.0")
    parser.add_argument("-v", "--version", action="version", version="0.1.0")
    parser.add_argument(
        "-d",
        "--domain",
        type=str,
        help="目标域名,eg: https://www.baidu.com,https://bing.com",
        required=True,
    )
    args = parser.parse_args()
    logger.info("开始加载指纹库")
    init()
    urls = args.domain.split(",")
    print(urls)
    async_run(urls)
    with open("errfinger.json", "w", encoding="utf-8") as f:
        json.dump(ErrFingers, f, indent=4, ensure_ascii=False)

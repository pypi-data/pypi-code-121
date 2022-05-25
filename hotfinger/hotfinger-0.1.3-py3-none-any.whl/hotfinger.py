#!/usr/bin/env python
# coding=utf-8

"""
Version: 0.1
Autor: zmf96
Email: zmf96@qq.com
Date: 2022-02-24 07:52:34
LastEditors: zmf96
LastEditTime: 2022-03-30 19:27:37
FilePath: /hotfinger/hotfinger.py
Description: 
"""
import argparse
import hashlib
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger
from Wappalyzer import Wappalyzer, WebPage

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TODO: 获取目标网站基础信息
# TODO: 使用自研引擎识别网站类型
# TODO: 使用wappalyzer/webanalyzer识别网站类型

path_finger = {}
basedir = os.path.dirname(os.path.abspath(__file__))

ErrFingers = []

# re
retitle = re.compile(r'title="(.*)"')
reheader = re.compile(r'header="(.*)"')
rebody = re.compile(r'body="(.*)"')
rebanner = re.compile(r"banner=(.*)")
reother = re.compile(r'^(.*?)="(.*)"')
rebracket = re.compile(r"\((.*)\)")


class PathHotFinger:
    def __init__(self):
        self.url = ""
        self.title = ""
        self.headers = ""
        self.response = None
        self.response_size = 0
        self.body = ""
        self.body_md5 = ""
        self.status_code = 0
        self.fingers = []

    def run(self, url, fingers):
        self.url = url
        self._get_webpage()
        self._run(fingers)
        self._run_wappalyzer()
        self._run_webanalyzer()
        self.fingers = list(set(self.fingers))

    def _get_webpage(self):
        try:
            resp = requests.get(
                self.url,
                headers=self.requests_headers(),
                verify=False,
                timeout=10,
                allow_redirects=True,
            )
            self.response = resp
            _bs = BeautifulSoup(resp.text, "html5lib")  # 创建BeautifulSoup对象
            self.title = _bs.title.string if _bs.title else ""
            logger.debug(self.title)
            self.headers = str(resp.headers)
            self.response = resp
            self.response_size = len(resp.text)
            self.body = resp.text
            self.body_md5 = self._get_md5(self.body)
            self.status_code = resp.status_code
        except Exception as e:
            logger.warning(e)

    def _check_rule(self, rule):
        try:
            if 'title="' in rule:
                title_value = re.findall(retitle, rule)
                if title_value[0].lower().strip() in self.title.lower():
                    return True
            elif 'body="' in rule:
                body_value = re.findall(rebody, rule)
                # st = rule.strip('() ')[6:-1]
                # if body_value[0] != st:
                #     logger.info(rule)
                #     logger.warning(body_value)
                #     logger.warning(st)
                if body_value[0] in self.body:
                    return True
            elif "header=" in rule:
                if re.findall(reheader, rule)[0] in self.headers:
                    return True
            elif "banner=" in rule:
                if re.findall(rebanner, rule)[0] in self.body:
                    return True
            else:
                # logger.warning(rule)
                # logger.info(re.findall(reother,rule))
                if re.findall(reother, rule)[0][1] in self.headers:
                    return True
                return False

        except Exception as e:
            logger.warning(e)
            logger.debug(rule)
            return 0

    def _handle(self, name, content):
        # 满足一个条件即可的情况 1||2||3
        if (
            "||" in content
            and "&&" not in content
            and ("(" not in content or ")" not in content)
        ):
            for rule in content.split("||"):
                cr_ret = self._check_rule(rule)
                if cr_ret == True:
                    self.fingers.append(name)
                    break
                elif cr_ret == 0:
                    ErrFingers.append({name: content})
        # 只有一个条件的情况  1
        elif "||" not in content and "&&" not in content and "(" not in content:
            if self._check_rule(content):
                self.fingers.append(name)
        # 需要同时满足条件的情况 1&&2&&3
        elif "&&" in content and "||" not in content and "(" not in content:
            num = 0
            for rule in content.split("&&"):
                cr_ret = self._check_rule(rule)
                if cr_ret == True:
                    num += 1
                elif cr_ret == 0:
                    ErrFingers.append({name: content})
            if num == len(content.split("&&")):
                self.fingers.append(name)
        else:
            # 与条件下存在并条件: 1||2||(3&&4)
            if "&&" in re.findall(rebracket, content)[0]:
                for rule in content.split("||"):
                    if "&&" in rule:
                        num = 0
                        for _rule in rule.split("&&"):
                            cr_ret = self._check_rule(_rule)
                            if cr_ret == True:
                                num += 1
                            elif cr_ret == 0:
                                ErrFingers.append({name: content})
                        if num == len(rule.split("&&")):
                            self.fingers.append(name)
                            break
                    else:
                        cr_ret = self._check_rule(rule)
                        if cr_ret == True:
                            self.fingers.append(name)
                            break
                        elif cr_ret == 0:
                            ErrFingers.append({name: content})
            else:
                # 并条件下存在与条件： 1&&2&&(3||4)
                for rule in content.split("&&"):
                    num = 0
                    if "||" in rule:
                        for _rule in rule.split("||"):
                            cr_ret = self._check_rule(_rule)
                            if cr_ret == True:
                                num += 1
                            elif cr_ret == 0:
                                ErrFingers.append({name: content})
                    else:
                        cr_ret = self._check_rule(rule)
                        if cr_ret == True:
                            num += 1
                        elif cr_ret == 0:
                            ErrFingers.append({name: content})
                if num == len(content.split("&&")):
                    self.fingers.append(name)

    def _run(self, fingers):
        for item in fingers:
            try:
                for name, finger in item.items():
                    self._handle(name, finger)
            except Exception as e:
                logger.info(item)
                logger.info(finger)
                ErrFingers.append(item)
                logger.warning(e)

    def _run_wappalyzer(self):
        webpage = WebPage.new_from_response(self.response)
        wappalyzer = Wappalyzer.latest()
        ret = wappalyzer.analyze(webpage)
        self.fingers.extend(ret)

    def _run_webanalyzer(self):
        pass

    @staticmethod
    def requests_headers():
        user_agent = [
            "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0",
            "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.6 Safari/532.0",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1 ; x64; en-US; rv:1.9.1b2pre) Gecko/20081026 Firefox/3.1b2pre",
            "Opera/10.60 (Windows NT 5.1; U; zh-cn) Presto/2.6.30 Version/10.60",
            "Opera/8.01 (J2ME/MIDP; Opera Mini/2.0.4062; en; U; ssr)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; ; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4 ( .NET CLR 3.5.30729)",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5",
        ]
        UA = random.choice(user_agent)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": UA,
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "http://www.baidu.com/",
        }
        return headers

    @staticmethod
    def requests_proxies():
        proxies = {"http": "", "https": ""}  # 127.0.0.1:1080
        return proxies

    @staticmethod
    def _get_md5(text):
        m = hashlib.md5()
        m.update(text.encode("utf-8"))
        return m.hexdigest()


class HotFinger:
    def __init__(self):
        self.url = ""
        self.fingers = []
        self.pages = dict()

    def run(self, url):
        self.url = url
        try:
            path_hot_finger = PathHotFinger()
            for path, fingers in path_finger.items():
                path_hot_finger.run(url + path, fingers)
                self.fingers.extend(path_hot_finger.fingers)
                self.pages[path] = path_hot_finger
        except Exception as e:
            print(e)


def init(fingers=[]):
    if fingers == []:
        with open(
            os.path.join(basedir, "data", "hotfinger_v3.json"), "r", encoding="utf-8"
        ) as f:
            fingers = json.load(f)
    logger.info("指纹数量" + str(len(fingers)))
    global path_finger
    path_finger = {}
    for item in fingers:
        for path, finger in item["content"].items():
            if path in path_finger.keys():
                path_finger[path].append({item["name"]: finger})
            else:
                path_finger[path] = [{item["name"]: finger}]


def worker(url):
    hf = HotFinger()
    hf.run(url)
    return hf


def async_run(urls: list) -> list:
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(worker, url): url for url in urls}
        for future in as_completed(future_to_url):
            logger.info(future_to_url[future])
            logger.info(future.result().fingers)

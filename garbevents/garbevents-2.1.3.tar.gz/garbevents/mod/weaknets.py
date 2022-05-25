#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2022/5/6 9:52 上午
@Desc    :  weak net line.
"""

import re
import time
import typing

from mitmproxy import ctx, exceptions, flowfilter
from mitmproxy.utils.spec import parse_spec

bandwidth_type = [
    {
        "template_name": "2G",
        "bandwidth": 10,
        "display": "2G (10 Kb/s)"
    }, {
        "template_name": "2.5G",
        "bandwidth": 35,
        "display": "2.5G (35 Kb/s)"
    },
    {
        "template_name": "3G",
        "bandwidth": 120,
        "display": "3G (120 Kb/s)"
    }
]
indexes_by_name = {i["template_name"]: i["bandwidth"] for i in bandwidth_type}


class WeakNetsSpec(typing.NamedTuple):
    matches: flowfilter.TFilter
    subject: str
    bandwidth: str


def parse_weak_net_spec(option: str) -> WeakNetsSpec:
    """

    :param option:
    :return:
    """
    spec = WeakNetsSpec(*parse_spec(option))

    try:
        re.compile(spec.subject)
    except re.error as e:
        raise ValueError(f"Invalid regular expression {spec.subject!r} ({e})")

    if not indexes_by_name.get(spec.bandwidth):
        raise ValueError(f"Invalid bandwidth type {spec.bandwidth!r}")

    return spec


class WeakNets:
    def __init__(self):
        self.bandwidth_templates: typing.List[WeakNetsSpec] = []

    def load(self, loader):
        loader.add_option(
            "weak_nets", typing.Sequence[str], [],
            """
            使用"|flow-filter|url-regex|bandwidth"形式的模式限制网络带宽，其中分隔符是|，支持模拟 2G,2.5G,3G 带宽。
            """
        )

    def configure(self, updated):
        if "weak_nets" in updated:
            self.bandwidth_templates = []
            for option in ctx.options.weak_nets:
                try:
                    spec = parse_weak_net_spec(option)
                except ValueError as e:
                    raise exceptions.OptionsError(f"Cannot parse weak_nets option {option}: {e}") from e

                self.bandwidth_templates.append(spec)

    def request(self, flow):
        if flow.response or flow.error or not flow.live:
            return
        self.run(flow)

    def response(self, flow):
        if flow.error or not flow.live:
            return
        self.run(flow)

    def run(self, flow):
        for spec in self.bandwidth_templates:
            if spec.matches(flow):
                chunk_size = 2048
                if flow.response:
                    try:
                        length = len(flow.response.headers['Content-length'])
                    except (ValueError, UnicodeDecodeError, KeyError):
                        length = 0
                    sleep_time = chunk_size / (indexes_by_name.get(spec.bandwidth) * 1024)
                    for i in range(int(length / chunk_size) + 1):
                        time.sleep(sleep_time)
                else:
                    try:
                        length = len(flow.request.headers['Content-length'])
                    except (ValueError, UnicodeDecodeError, KeyError):
                        length = 0
                    sleep_time = chunk_size / (indexes_by_name.get(spec.bandwidth) * 1024)
                    for i in range(int(length / chunk_size) + 1):
                        time.sleep(sleep_time)

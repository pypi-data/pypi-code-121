#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2022/5/5 11:31 上午
@Desc    :  map remote line.
"""

import re
import typing

from mitmproxy import ctx, exceptions, flowfilter, http
from mitmproxy.utils.spec import parse_spec


class MapRemotesSpec(typing.NamedTuple):
    matches: flowfilter.TFilter
    subject: str
    replacement: str


def parse_map_remote_spec(option: str) -> MapRemotesSpec:
    spec = MapRemotesSpec(*parse_spec(option))

    try:
        re.compile(spec.subject)
    except re.error as e:
        raise ValueError(f"Invalid regular expression {spec.subject!r} ({e})")

    return spec


class MapRemotes:
    def __init__(self):
        self.replacements: typing.List[MapRemotesSpec] = []

    def load(self, loader):
        loader.add_option(
            "map_remotes", typing.Sequence[str], [],
            """
            使用"|flow-filter|url-regex|replacement"形式的模式将远程资源映射到另一个远程 URL，其中分隔符是|。
            """
        )

    def configure(self, updated):
        if "map_remotes" in updated:
            self.replacements = []
            for option in ctx.options.map_remotes:
                try:
                    spec = parse_map_remote_spec(option)
                except ValueError as e:
                    raise exceptions.OptionsError(f"Cannot parse map_remotes option {option}: {e}") from e

                self.replacements.append(spec)

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.response or flow.error or not flow.live:
            return
        for spec in self.replacements:
            if spec.matches(flow):
                url = flow.request.pretty_url
                new_url = re.sub(spec.subject, spec.replacement, url)
                if url != new_url:
                    flow.request.url = new_url  # type: ignore

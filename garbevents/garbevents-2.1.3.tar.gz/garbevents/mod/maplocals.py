#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2022/5/5 1:48 下午
@Desc    :  map local line.
"""
import getpass
import mimetypes
import platform
import re
import typing
import urllib.parse
from pathlib import Path

from werkzeug.security import safe_join

from mitmproxy import ctx, exceptions, flowfilter, http, version
from mitmproxy.utils.spec import parse_spec


class MapLocalsSpec(typing.NamedTuple):
    matches: flowfilter.TFilter
    regex: str
    local_path: Path


def parse_map_local_spec(option: str) -> MapLocalsSpec:
    filter, regex, replacement = parse_spec(option)

    try:
        re.compile(regex)
    except re.error as e:
        raise ValueError(f"Invalid regular expression {regex!r} ({e})")

    try:
        if platform.system() != 'Darwin':
            path = Path(replacement).expanduser().resolve(strict=True)
        else:
            default = f'/Users/{getpass.getuser()}/Documents/map_local/'
            path = Path(default + replacement).expanduser().resolve(strict=True)
    except FileNotFoundError as e:
        raise ValueError(f"Invalid file path: {replacement} ({e})")

    return MapLocalsSpec(filter, regex, path)


def _safe_path_join(root: Path, untrusted: str) -> Path:
    """Join a Path element with an untrusted str.

    This is a convenience wrapper for werkzeug's safe_join,
    raising a ValueError if the path is malformed."""
    untrusted_parts = Path(untrusted).parts
    joined = safe_join(
        root.as_posix(),
        *untrusted_parts
    )
    if joined is None:
        raise ValueError("Untrusted paths.")
    return Path(joined)


def file_candidates(url: str, spec: MapLocalsSpec) -> typing.List[Path]:
    """
    Get all potential file candidates given a URL and a mapping spec ordered by preference.
    This function already assumes that the spec regex matches the URL.
    """
    m = re.search(spec.regex, url)
    assert m
    if m.groups():
        suffix = m.group(1)
    else:
        suffix = re.split(spec.regex, url, maxsplit=1)[1]
        suffix = suffix.split("?")[0]  # remove query string
        suffix = suffix.strip("/")

    if suffix:
        decoded_suffix = urllib.parse.unquote(suffix)
        suffix_candidates = [decoded_suffix, f"{decoded_suffix}/index.html"]

        escaped_suffix = re.sub(r"[^0-9a-zA-Z\-_.=(),/]", "_", decoded_suffix)
        if decoded_suffix != escaped_suffix:
            suffix_candidates.extend([escaped_suffix, f"{escaped_suffix}/index.html"])
        try:
            return [
                _safe_path_join(spec.local_path, x)
                for x in suffix_candidates
            ]
        except ValueError:
            return []
    else:
        return [spec.local_path / "index.html"]


class MapLocals:
    def __init__(self):
        self.replacements: typing.List[MapLocalsSpec] = []

    def load(self, loader):
        loader.add_option(
            "map_locals", typing.Sequence[str], [],
            """
            使用"|flow-filter|url-regex|file-or-directory-path"形式的模式将远程资源映射到本地文件，其中分隔符是|。
            """
        )

    def configure(self, updated):
        if "map_locals" in updated:
            self.replacements = []
            for option in ctx.options.map_locals:
                try:
                    spec = parse_map_local_spec(option)
                except ValueError as e:
                    raise exceptions.OptionsError(f"Cannot parse map_locals option {option}: {e}") from e

                self.replacements.append(spec)

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.response or flow.error or not flow.live:
            return

        url = flow.request.pretty_url

        all_candidates = []
        for spec in self.replacements:
            if spec.matches(flow) and re.search(spec.regex, url):
                if spec.local_path.is_file():
                    candidates = [spec.local_path]
                else:
                    candidates = file_candidates(url, spec)
                all_candidates.extend(candidates)

                local_file = None
                for candidate in candidates:
                    if candidate.is_file():
                        local_file = candidate
                        break

                if local_file:
                    headers = {
                        "Server": version.MITMPROXY
                    }
                    mimetype = mimetypes.guess_type(str(local_file))[0]
                    if mimetype:
                        headers["Content-Type"] = mimetype

                    try:
                        contents = local_file.read_bytes()
                    except OSError as e:
                        ctx.log.warn(f"Could not read file: {e}")
                        continue

                    flow.response = http.Response.make(
                        200,
                        contents,
                        headers
                    )
                    # only set flow.response once, for the first matching rule
                    return
        if all_candidates:
            flow.response = http.Response.make(404)
            ctx.log.info(f"None of the local file candidates exist: {', '.join(str(x) for x in all_candidates)}")
